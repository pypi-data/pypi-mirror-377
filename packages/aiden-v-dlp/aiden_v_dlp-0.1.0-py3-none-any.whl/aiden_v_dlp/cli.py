import sys, shutil, subprocess, os
from pathlib import Path

DEFAULTS = [
    "-o", str(Path.home() / "Downloads" / "%(title)s.%(ext)s"),
    "-f", "mp4/bestvideo+bestaudio/best",
]

def main():
    # Pass-through if user provides advanced flags; otherwise apply your defaults.
    user_args = sys.argv[1:]
    if not user_args or user_args[0].startswith("-"):
        args = DEFAULTS + user_args
    else:
        # If first arg looks like a URL, still apply sane defaults
        args = DEFAULTS + user_args

    yt = shutil.which("yt-dlp")
    if yt is None:
        print("yt-dlp not found. Installing tip: `pipx install yt-dlp` or `pip install yt-dlp`.", file=sys.stderr)
        sys.exit(1)

    # Hand off to yt-dlp CLI (most compatible)
    raise SystemExit(subprocess.call([yt, *args]))
