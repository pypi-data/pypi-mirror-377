#!/usr/bin/env python3
"""
downloader.py — VPS download-only helpers for yt-dlp (no transcoding here).

Intended usage:
    from downloader import download_video
    path = download_video(url, resolution=1080, extension="mp4", out_dir="/root")

Design:
- No Flask / no __main__; pure library module.
- Connects via Mullvad (optional but recommended) and pins an exit location to
  improve 1080p availability.
- Uses yt-dlp to fetch best <= <resolution> (any codec), embedding metadata.
- For audio "mp3", uses -x --audio-format mp3; otherwise bestaudio/as needed.
- Returns the final file path on success; raises RuntimeError on hard failures.

Environment variables:
- YTPDL_VENV               (default: /opt/yt-dlp-mullvad/venv)
- YTPDL_MULLVAD_LOCATION   (default: "us")
- YTPDL_USER_AGENT         (override the default UA)
"""

from __future__ import annotations
import os
import shlex
import shutil
import subprocess
import time
from typing import Optional

# =========================
# Config / constants
# =========================
VENV_PATH = os.environ.get("YTPDL_VENV", "/opt/yt-dlp-mullvad/venv")
YTDLP_BIN = os.path.join(VENV_PATH, "bin", "yt-dlp")
MULLVAD_LOCATION = os.environ.get("YTPDL_MULLVAD_LOCATION", "us")
MODERN_UA = os.environ.get(
    "YTPDL_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# =========================
# Shell helpers
# =========================
def _run(cmd: str, check: bool = True) -> str:
    """Run a shell command; return stdout; raise on error if check=True."""
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{res.stdout}")
    return res.stdout

def _run_argv(argv: list[str], check: bool = True) -> str:
    """Run an argv command; return stdout; raise on error if check=True."""
    res = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if check and res.returncode != 0:
        cmd = " ".join(shlex.quote(p) for p in argv)
        raise RuntimeError(f"Command failed: {cmd}\n{res.stdout}")
    return res.stdout

# =========================
# Environment / yt-dlp / Mullvad
# =========================
def validate_environment() -> None:
    """Ensure venv + yt-dlp exist."""
    if not os.path.isdir(VENV_PATH):
        raise RuntimeError(
            "Virtualenv missing. Create and install yt-dlp:\n"
            f"  python3 -m venv {VENV_PATH}\n"
            f"  source {VENV_PATH}/bin/activate\n"
            "  pip install -U yt-dlp"
        )
    if not os.path.exists(YTDLP_BIN):
        raise RuntimeError(f"yt-dlp not found at {YTDLP_BIN}. Install inside the venv.")

def _mullvad_present() -> bool:
    return shutil.which("mullvad") is not None

def mullvad_logged_in() -> bool:
    """Return True if `mullvad account get` says we're logged in."""
    if not _mullvad_present():
        return False
    out = _run("mullvad account get", check=False)
    return "not logged in" not in (out or "").lower()

def require_mullvad_login() -> None:
    """Raise if Mullvad CLI is present but not logged in."""
    if _mullvad_present() and not mullvad_logged_in():
        raise RuntimeError(
            "Mullvad is not logged in on this server.\n"
            "Run once via SSH:  mullvad account login <ACCOUNT>"
        )

def mullvad_connect(location: Optional[str] = None) -> None:
    """Pin relay location and connect. No-op if Mullvad not installed."""
    if not _mullvad_present():
        return
    loc = (location or MULLVAD_LOCATION).strip()
    _run("mullvad disconnect", check=False)
    if loc:
        _run(f"mullvad relay set location {shlex.quote(loc)}", check=False)
    _run("mullvad connect", check=False)

def mullvad_wait_connected(timeout: int = 10) -> bool:
    """Wait for Mullvad to report 'Connected'. True if connected."""
    if not _mullvad_present():
        return True
    for _ in range(timeout):
        out = _run("mullvad status", check=False)
        if "Connected" in (out or ""):
            return True
        time.sleep(1)
    return False

# =========================
# yt-dlp helpers
# =========================
def _extract_downloaded_filename(stdout: str) -> Optional[str]:
    """
    Parse yt-dlp stdout to get the destination filename.
    Handles both fresh downloads and "already downloaded".
    """
    name = None
    for line in (stdout or "").splitlines():
        if not line.startswith("[download]"):
            continue
        if "Destination:" in line:
            name = line.split("Destination: ", 1)[1].strip()
        elif " has already been downloaded" in line and "] " in line:
            start = line.find("] ") + 2
            end = line.rfind(" has already been downloaded")
            name = line[start:end].strip().strip("'")
        if name:
            break
    return name

def _common_flags() -> str:
    return (
        "--retries 6 --fragment-retries 6 --retry-sleep 2 "
        f"--user-agent '{MODERN_UA}' "
        "--no-cache-dir --ignore-config --embed-metadata"
    )

# =========================
# Public API
# =========================
def download_video(
    url: str,
    resolution: int | None = 1080,
    extension: Optional[str] = None,
    out_dir: str = "/root"
) -> str:
    """
    Download media using yt-dlp with no transcoding.

    Args:
        url: Source URL (YouTube or other supported site).
        resolution: Max video height (default 1080). Ignored for audio-only.
        extension: If "mp3", extract audio as MP3. If None or "mp4", download best video.
        out_dir: Destination directory (created if missing).

    Returns:
        Absolute path to the downloaded file.

    Raises:
        RuntimeError: on environment, VPN, or download errors.
    """
    if not url:
        raise RuntimeError("Missing URL.")
    os.makedirs(out_dir, exist_ok=True)

    validate_environment()
    require_mullvad_login()

    # VPN (optional but recommended): pin exit and connect
    mullvad_connect(MULLVAD_LOCATION)
    if not mullvad_wait_connected():
        raise RuntimeError("Could not establish Mullvad VPN connection.")

    try:
        # Audio-only fast path
        if extension and extension.lower() == "mp3":
            out_tpl = os.path.join(out_dir, "%(title)s.%(ext)s")
            cmd = (
                f"{shlex.quote(YTDLP_BIN)} -x --audio-format mp3 "
                f"{_common_flags()} "
                f"--output {shlex.quote(out_tpl)} {shlex.quote(url)}"
            )
            out = _run(cmd)
            path = _extract_downloaded_filename(out)
            if not path or not os.path.exists(path):
                raise RuntimeError("Audio download finished but file not found.")
            return os.path.abspath(path)

        # Video path (any codec, <= resolution)
        cap = int(resolution or 1080)
        out_tpl = os.path.join(out_dir, "%(title)s.%(ext)s")
        fmt = f"bv*[height<={cap}]+ba/b[height<={cap}]"
        sort = '-S "res,fps,br,filesize"'
        cmd = (
            f'{shlex.quote(YTDLP_BIN)} -f "{fmt}" {sort} '
            f"{_common_flags()} "
            f"--output {shlex.quote(out_tpl)} {shlex.quote(url)}"
        )

        out = _run(cmd)
        path = _extract_downloaded_filename(out)
        if not path or not os.path.exists(path):
            raise RuntimeError("Video download finished but file not found.")
        return os.path.abspath(path)

    finally:
        # Always disconnect; caller controls when to reconnect for next job.
        _run("mullvad disconnect", check=False)
