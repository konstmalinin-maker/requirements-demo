"""Shared definitions: headings declare requirements; collected pytest tests prove links."""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"\b(?:BR|UR|FR|NFR)-\d{3}\b")
HEADING = re.compile(r"^## ((?:BR|UR|FR|NFR)-\d{3})@v(\d+): (.+)$", re.MULTILINE)
REPO = "https://github.com/konstmalinin-maker/requirements-demo"


def definitions(root=ROOT):
    result = {}
    for path in sorted((root / "docs/requirements").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        matches = list(HEADING.finditer(text))
        for i, match in enumerate(matches):
            rid, version, title = match.groups()
            if rid in result:
                raise ValueError(f"Duplicate requirement definition: {rid}")
            block = text[
                match.end() : matches[i + 1].start() if i + 1 < len(matches) else len(text)
            ]
            priority = re.search(r"\*\*Приоритет:\*\* (Must|Should|Could)", block)
            if not priority:
                raise ValueError(f"Missing priority: {rid}")
            result[rid] = {
                "version": int(version),
                "title": title,
                "priority": priority[1],
                "path": str(path.relative_to(root)),
                "body": block.strip(),
            }
    return result


def registry(root=ROOT):
    return json.loads((root / "docs/requirements/registry.json").read_text())


def commits(root=ROOT):
    process = subprocess.run(
        ["git", "log", "--pretty=%H|%s|%an|%ad", "--date=iso-strict"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    rows = []
    for line in process.stdout.splitlines():
        sha, subject, author, date = line.split("|", 3)
        if subject.startswith("chore(rtm):"):
            continue  # Generated documents must not refer to their own new commit SHA.
        paths = subprocess.run(
            ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", sha],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
        rows.append(
            {
                "sha": sha,
                "subject": subject,
                "author": author,
                "date": date,
                "requirements": sorted(set(ID.findall(subject))),
                "paths": paths,
            }
        )
    return rows


def test_links(root=ROOT):
    with tempfile.TemporaryDirectory(prefix="req-collection-") as temporary:
        target = Path(temporary) / "links.json"
        process = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "--req-map", str(target)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if process.returncode or not target.exists():
            raise ValueError("Cannot collect pytest links:\n" + process.stdout + process.stderr)
        return json.loads(target.read_text())


def source_commits(rows, rid):
    return [
        r
        for r in rows
        if rid in r["requirements"]
        and any(
            p.startswith(("src/", "tests/", "scripts/", ".github/"))
            or p in ("pyproject.toml", "requirements.txt")
            for p in r["paths"]
        )
    ]
