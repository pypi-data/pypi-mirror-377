#!/usr/bin/env python3
"""
downloader.py — VPS download-only helpers for yt-dlp (no transcoding here).

Strategy:
1) If extension == "mp3": extract audio to MP3 (fast).
2) Else (video): TRY H.264<=1080 + AAC (mp4/m4a) FIRST, with --merge-output-format mp4.
   If that selection isn't available, FALL BACK to best<=1080 any codec.
   Returning MP4/H.264 reduces or eliminates iOS transcode on the main server.

Env:
- YTPDL_VENV               (default: /opt/yt-dlp-mullvad/venv)
- YTPDL_MULLVAD_LOCATION   (default: "us")
- YTPDL_USER_AGENT         (override UA)
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
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{res.stdout}")
    return res.stdout

def _run_argv(argv: list[str], check: bool = True) -> str:
    res = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if check and res.returncode != 0:
        cmd = " ".join(shlex.quote(p) for p in argv)
        raise RuntimeError(f"Command failed: {cmd}\n{res.stdout}")
    return res.stdout

# =========================
# Environment / yt-dlp / Mullvad
# =========================
def validate_environment() -> None:
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
    if not _mullvad_present():
        return False
    out = _run("mullvad account get", check=False)
    return "not logged in" not in (out or "").lower()

def manual_login(mullvad_account: str) -> None:
    if not _mullvad_present():
        raise RuntimeError("Mullvad CLI not installed on this host.")
    if not mullvad_account:
        raise RuntimeError("Missing Mullvad account number.")
    out = _run("mullvad account get", check=False)
    if "not logged in" not in (out or "").lower():
        print("Already logged into Mullvad.")
        return
    _run(f"mullvad account login {shlex.quote(mullvad_account)}")
    print("Mullvad login complete (no VPN connection started).")

def require_mullvad_login() -> None:
    if _mullvad_present() and not mullvad_logged_in():
        raise RuntimeError(
            "Mullvad is not logged in on this server.\n"
            "Run once via SSH:  mullvad account login <ACCOUNT>"
        )

def mullvad_connect(location: Optional[str] = None) -> None:
    if not _mullvad_present():
        return
    loc = (location or MULLVAD_LOCATION).strip()
    _run("mullvad disconnect", check=False)
    if loc:
        _run(f"mullvad relay set location {shlex.quote(loc)}", check=False)
    _run("mullvad connect", check=False)

def mullvad_wait_connected(timeout: int = 10) -> bool:
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

def _try_h264_first(url: str, out_tpl: str, cap: int) -> Optional[str]:
    """
    Try hard for H.264 (avc1) video + AAC audio <=cap, merge to MP4.
    If formats not available, return None so caller can fallback.
    """
    # Prefer H.264 by sort, and explicitly restrict via vcodec/acodec regex.
    # Use res:1080 in sort to push 1080p when multiple H.264 streams exist.
    fmt = (
        f"bv*[height<={cap}][vcodec~='^(?:avc1|h264)']"
        f"+ba[acodec~='^mp4a']/"
        f"b[height<={cap}][vcodec~='^(?:avc1|h264)']"
    )
    sort = '-S "codec:h264,res:1080,fps,br,filesize"'
    cmd = (
        f'{shlex.quote(YTDLP_BIN)} -f "{fmt}" {sort} '
        f"{_common_flags()} "
        f"--merge-output-format mp4 "
        f"--output {shlex.quote(out_tpl)} {shlex.quote(url)}"
    )
    out = _run(cmd, check=False)
    # If yt-dlp couldn't find a matching format, it typically exits non-zero with an error.
    # We only accept it if we can parse a destination file that exists.
    path = _extract_downloaded_filename(out)
    return path if (path and os.path.exists(path)) else None

# =========================
# Public API
# =========================
def download_video(
    url: str,
    resolution: int | None = 1080,
    extension: Optional[str] = None,
    out_dir: str = "/root",
) -> str:
    """
    Download media using yt-dlp with no transcoding.

    Args:
        url: Source URL.
        resolution: Max video height (default 1080). Ignored for audio-only.
        extension: "mp3" => extract audio; otherwise video.
        out_dir: Target dir.

    Returns:
        Absolute path to the downloaded file.

    Raises:
        RuntimeError on errors.
    """
    if not url:
        raise RuntimeError("Missing URL.")
    os.makedirs(out_dir, exist_ok=True)

    validate_environment()
    require_mullvad_login()

    mullvad_connect(MULLVAD_LOCATION)
    if not mullvad_wait_connected():
        raise RuntimeError("Could not establish Mullvad VPN connection.")

    try:
        # ---------- Audio-only ----------
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

        # ---------- Video (H.264-first, then fallback) ----------
        cap = int(resolution or 1080)
        out_tpl = os.path.join(out_dir, "%(title)s.%(ext)s")

        # A) H.264 (avc1) + AAC ≤cap, MP4 container
        h264_path = _try_h264_first(url, out_tpl, cap)
        if h264_path:
            return os.path.abspath(h264_path)

        # B) Fallback: best ≤cap (any codec/container)
        fmt_any = f"bv*[height<={cap}]+ba/b[height<={cap}]"
        sort_any = '-S "res,fps,br,filesize"'
        cmd_any = (
            f'{shlex.quote(YTDLP_BIN)} -f "{fmt_any}" {sort_any} '
            f"{_common_flags()} "
            f"--output {shlex.quote(out_tpl)} {shlex.quote(url)}"
        )
        out = _run(cmd_any)
        path = _extract_downloaded_filename(out)
        if not path or not os.path.exists(path):
            raise RuntimeError("Video download finished but file not found.")
        return os.path.abspath(path)

    finally:
        _run("mullvad disconnect", check=False)
