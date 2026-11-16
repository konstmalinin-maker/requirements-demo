"""FR-001…FR-005, NFR-004, NFR-006: русскоязычный CLI."""

import argparse
import os
import sys
from pathlib import Path

from src.exporters import ExportRegistry
from src.messages import UserError, message
from src.note_manager import NoteManager
from src.storage import JsonStorage


class RussianParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._optionals.title = message("arguments")
        self._positionals.title = message("commands")
        self._actions[0].help = message("help")

    def format_usage(self):
        return super().format_usage().replace("usage: ", message("usage"))

    def format_help(self):
        return super().format_help().replace("usage: ", message("usage"))

    def error(self, _details):
        raise UserError(message("bad_arguments"))


def parser():
    cli = RussianParser(prog="note", description=message("description"))
    cli.add_argument(
        "--storage",
        type=Path,
        help=message("storage_help"),
        default=Path(os.environ.get("NOTES_FILE", "~/.notes.json")).expanduser(),
    )
    commands = cli.add_subparsers(dest="command", required=True)
    for name in ["add", "list", "search", "edit", "delete", "export"]:
        sub = commands.add_parser(
            name, help=message(f"{name}_help"), description=message(f"{name}_help")
        )
        if name in ("edit", "delete"):
            sub.add_argument("id", help=message("id_help"))
        if name in ("add", "edit"):
            sub.add_argument("--title", required=name == "add", help=message("title_help"))
            sub.add_argument("--body", required=name == "add", help=message("body_help"))
        if name == "search":
            sub.add_argument("--query", required=True, help=message("query_help"))
        if name == "export":
            sub.add_argument("--format", default="json", help=message("format_help"))
    return cli


def display(notes):
    if not notes:
        print(message("empty"))
        return
    print(message("header"))
    for note in notes:
        print(f"{note.id} | {note.title} | {note.created_at}")


def main(argv=None, input_fn=None) -> int:
    try:
        args = parser().parse_args(argv)
        manager = NoteManager(JsonStorage(args.storage))
        if args.command == "add":
            note = manager.add_note(args.title, args.body)
            print(message("created", id=note.id))
        elif args.command == "list":
            display(manager.list_notes())
        elif args.command == "search":
            display(manager.search_notes(args.query))
        elif args.command == "edit":
            note = manager.edit_note(args.id, args.title, args.body)
            print(message("updated", id=note.id))
        elif args.command == "delete":
            try:
                answer = (input_fn or input)(message("confirm"))
            except EOFError:
                answer = ""
            if answer.strip().casefold() not in ("да", "yes"):
                print(message("cancelled"))
                return 0
            manager.delete_note(args.id)
            print(message("deleted", id=args.id))
        elif args.command == "export":
            print(ExportRegistry().export(manager.list_notes(), args.format))
        return 0
    except UserError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError:
        print(message("io_error"), file=sys.stderr)
        return 2


def entrypoint():
    raise SystemExit(main())


if __name__ == "__main__":
    entrypoint()
