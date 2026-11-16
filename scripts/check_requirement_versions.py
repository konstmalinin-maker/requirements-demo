"""Extra G: compare every requirement body with the base commit, enforcing +1 versions."""

import argparse
import subprocess
import sys

from traceability_lib import HEADING, ROOT, definitions, registry


def at_revision(ref, root=ROOT):
    files = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "docs/requirements"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    result = {}
    for path in files:
        if not path.endswith(".md"):
            continue
        text = subprocess.run(
            ["git", "show", f"{ref}:{path}"], cwd=root, capture_output=True, text=True, check=True
        ).stdout
        headings = list(HEADING.finditer(text))
        for i, h in enumerate(headings):
            body = text[h.end() : headings[i + 1].start() if i + 1 < len(headings) else len(text)]
            result[h[1]] = {"version": int(h[2]), "content": (h[3] + "\n" + body.strip()).strip()}
    return result


def check(base, root=ROOT):
    old = at_revision(base, root)
    new = definitions(root)
    meta = registry(root)
    errors = []
    for rid in sorted(old.keys() - new.keys()):
        errors.append(f"{rid}: удалено определение; сохраните ID со статусом retired")
    for rid, spec in sorted(new.items()):
        previous = old.get(rid)
        if meta.get(rid, {}).get("version") != spec["version"]:
            errors.append(f"{rid}: версия registry не совпадает")
        if previous:
            changed = previous["content"] != (spec["title"] + "\n" + spec["body"]).strip()
            wanted = previous["version"] + int(changed)
            if spec["version"] != wanted:
                errors.append(
                    f"{rid}: ожидалась v{wanted}, получена v{spec['version']}; changed={changed}"
                )
        elif spec["version"] != 1:
            errors.append(f"{rid}: новое требование начинается с @v1")
    if any(
        rid in old and old[rid]["content"] != (spec["title"] + "\n" + spec["body"]).strip()
        for rid, spec in new.items()
    ):
        changed_files = subprocess.run(
            ["git", "diff", "--name-only", base, "--", "docs/requirements/changelog.md"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        if not changed_files.strip():
            errors.append("При изменении требования обновите changelog.md")
    for error in errors:
        print("FAIL:", error)
    if not errors:
        print(f"PASS: версии {len(new)} требований проверены относительно {base[:12]}")
    return int(bool(errors))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    sys.exit(check(args.base))
