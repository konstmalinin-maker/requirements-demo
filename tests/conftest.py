"""Collect real pytest node IDs and their requirement markers for RTM."""

import json

import pytest

from src.note_manager import NoteManager
from src.storage import JsonStorage


def pytest_addoption(parser):
    parser.addoption("--req-map", default=None, help="Write collected test/REQ links as JSON")


def pytest_collection_finish(session):
    target = session.config.getoption("--req-map")
    if target:
        from pathlib import Path

        links = {
            item.nodeid: sorted(
                {str(req) for marker in item.iter_markers("req") for req in marker.args}
            )
            for item in session.items
        }
        Path(target).write_text(json.dumps(links, ensure_ascii=False, indent=2) + "\n")


@pytest.fixture
def manager(tmp_path):
    return NoteManager(JsonStorage(tmp_path / "notes.json"))
