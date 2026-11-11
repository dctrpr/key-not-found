#!/usr/bin/env python3
"""Replay the registered line comparison with list-valued review notes."""
import importlib.util
from pathlib import Path
import sys

source = Path(__file__).with_name("reconcile_issue24_line_start_audit.py")
spec = importlib.util.spec_from_file_location("registered_line_comparison", source)
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)
registered_validator = comparison.validate_reader


def validate_reader(document, *args):
    notes = document.get("notes")
    if isinstance(notes, list) and all(isinstance(note, str) for note in notes):
        document = {**document, "notes": "\n".join(notes)}
    return registered_validator(document, *args)


comparison.validate_reader = validate_reader

if __name__ == "__main__":
    sys.exit(comparison.main())
