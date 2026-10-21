"""Create a project without overwriting existing work."""
import argparse, json, shutil
from datetime import datetime, timezone
from pathlib import Path

def create(destination):
    root = Path(destination).expanduser().resolve()
    if root.exists():
        raise ValueError(f"Destination already exists: {root}")
    repo = Path(__file__).resolve().parents[1]
    shutil.copytree(repo / "templates/project", root)
    for p in root.rglob(".gitkeep"):
        p.unlink()
    (root / "01-recording/project.json").write_text(json.dumps({"eyeline": 2, "name": root.name, "created": datetime.now(timezone.utc).isoformat()}, indent=2), encoding="utf-8")
    shutil.copyfile(repo / "config/preferences.example.json", root / "preferences.json")
    shutil.copyfile(repo / "apps/teleprompter/AGENTS-project.md", root / "01-recording/AGENTS.md")
    return root

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    args = parser.parse_args()
    try: print(create(args.destination))
    except ValueError as e: parser.error(str(e))
