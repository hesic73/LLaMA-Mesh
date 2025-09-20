#!/usr/bin/env python3
import json
from pathlib import Path
import tyro


def collect(root: Path, output: Path = Path("objects_summary.json")) -> None:
    """
    Collect <subdir name>: <object> from <subdir>/results.json files
    and save to a JSON file.

    Args:
        root: Root directory containing subdirectories.
        output: Path to output JSON file. Default = objects_summary.json
    """
    result = {}
    for subdir in sorted(root.iterdir()):
        if subdir.is_dir():
            data = json.loads((subdir / "result.json").read_text())
            result[subdir.name] = data["object"]

    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved {len(result)} entries to {output}")


if __name__ == "__main__":
    tyro.cli(collect)
