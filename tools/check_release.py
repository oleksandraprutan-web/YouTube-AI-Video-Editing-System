"""Check the public tree for accidental private files, credentials and unconfigured skill changes."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SKILLS = {"writing", "recording", "cutting", "review", "design", "animation", "editor"}
MEDIA = {"editor-demo.gif", "teleprompter-demo.gif", "edge-trimming.gif", "take-files.png", "project-files.png", "edit-plan-architecture.png", "take-report-architecture.png", "tries-to-cut.png", "agent-cut-layers.png", "teleprompter-layers.png"}

def check(root=ROOT):
    errors = []
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if any(x in {".git", ".local", ".venv", "__pycache__", "node_modules"} for x in rel.parts): continue
        if p.is_symlink(): errors.append(f"symlink: {rel}"); continue
        if not p.is_file(): continue
        if p.name.startswith(".env") or p.suffix.lower() in {".wav", ".mov", ".mp4", ".mp3", ".key", ".pem", ".bak", ".log"}:
            errors.append(f"private/media file: {rel}")
        if p.suffix.lower() in {".png", ".gif", ".jpg"}:
            if rel.parent.as_posix() != "docs/media" or p.name not in MEDIA: errors.append(f"unapproved image: {rel}")
            continue
        try: text = p.read_text(encoding="utf-8")
        except UnicodeError: errors.append(f"unexpected binary: {rel}"); continue
        # Patterns assembled to avoid matching this checker itself.
        forbidden = [r"/"+"Users/", r"/"+"Volumes/", "Kyles"+" project", "nick"+"-voice", r"gh[pousr]_"+r"[A-Za-z0-9]{20,}", r"sk-"+r"[A-Za-z0-9]{24,}", "BEGIN "+"PRIVATE KEY"]
        for pattern in forbidden:
            if re.search(pattern, str(rel), re.I) or re.search(pattern, text, re.I): errors.append(f"sensitive pattern in {rel}")
        if rel.parts[0] == "skills":
            if len(rel.parts) != 3 or rel.parts[1] not in ALLOWED_SKILLS or rel.name != "SKILL.md" or "PLACEHOLDER — NOT CONFIGURED" not in text:
                errors.append(f"non-placeholder skill: {rel}")
    return errors

if __name__ == "__main__":
    errors = check()
    print("\n".join(errors) if errors else "Public-tree checks passed")
    sys.exit(bool(errors))
