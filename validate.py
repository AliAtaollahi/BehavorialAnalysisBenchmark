#!/usr/bin/env python3
"""Check the published cases against their prompts and recorded answers."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys

EXPECTED = {"true-positive": "YES", "true-negative": "NO", "false-negative": "YES"}
REQUIRED = {"program_1.rebeca", "program_2.rebeca", "observable_messages.txt", "prompt.txt"}


def validate(root: Path) -> dict:
    with (root / "answers.csv").open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = {"case", "model", "program 1", "program 2", "category", "expected answer", "Gemini", "ChatGPT", "Qwen"}
        if not columns <= set(reader.fieldnames or []):
            raise ValueError("answers.csv is missing required columns")
        rows = list(reader)
    names = [row["case"] for row in rows]
    if not names or len(names) != len(set(names)):
        raise ValueError("Case names must be nonempty and unique")
    directories = {p.name for p in (root / "cases").iterdir() if p.is_dir()}
    if set(names) != directories:
        raise ValueError("Case directories and answers.csv rows do not match")
    revisions: dict[str, str] = {}
    for row in rows:
        name = row["case"]
        if Path(name).name != name or name in {".", ".."}:
            raise ValueError(f"Invalid case name: {name!r}")
        folder = root / "cases" / name
        if not REQUIRED <= {p.name for p in folder.iterdir() if p.is_file()}:
            raise ValueError(f"Missing required file in {name}")
        if row["category"] not in EXPECTED or row["expected answer"] != EXPECTED[row["category"]]:
            raise ValueError(f"Invalid category/answer in {name}")
        prompt = (folder / "prompt.txt").read_text(encoding="utf-8-sig")
        for i in (1, 2):
            code = (folder / f"program_{i}.rebeca").read_text(encoding="utf-8-sig")
            end = "[Program 2]:" if i == 1 else "[Observable messages]:"
            try:
                embedded = prompt.split(f"[Program {i}]:", 1)[1].split(end, 1)[0]
            except IndexError as error:
                raise ValueError(f"Missing program marker in {name}/prompt.txt") from error
            # Recorded prompts sometimes indent the same program differently.
            normalized = " ".join(code.split())
            if not normalized or normalized != " ".join(embedded.split()):
                raise ValueError(f"Prompt/program {i} mismatch in {name}")
            revision = row[f"program {i}"]
            if revision in revisions and normalized != revisions[revision]:
                raise ValueError(f"Inconsistent copies of revision {revision}")
            revisions[revision] = normalized
        observables = (folder / "observable_messages.txt").read_text(encoding="utf-8-sig").strip()
        if not observables or observables not in prompt:
            raise ValueError(f"Prompt/observable mismatch in {name}")
        for model in ("Gemini", "ChatGPT", "Qwen"):
            if row[model] not in {"YES", "NO", ""}:
                raise ValueError(f"Invalid {model} answer in {name}")
    return {
        "cases": len(rows), "unique_revisions": len(revisions),
        "models": dict(sorted(Counter(row["model"] for row in rows).items())),
        "categories": dict(sorted(Counter(row["category"] for row in rows).items())),
        "expected_answers": dict(sorted(Counter(row["expected answer"] for row in rows).items())),
        "recorded_results": {
            model: {"correct": sum(row[model] == row["expected answer"] for row in rows),
                    "answered": sum(bool(row[model]) for row in rows), "total": len(rows)}
            for model in ("Gemini", "ChatGPT", "Qwen")
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.root), indent=2))
    except (OSError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
