#!/usr/bin/env python3
"""
downloader.py — VPS download-only helpers for yt-dlp (no transcoding here).

What changed (concurrency-safe Mullvad control):
- We now coordinate downloads with a process-wide lock + active-job counter.
- Only when the FIRST job begins do we rotate Mullvad (disconnect → connect).
- While any jobs are running, we DO NOT rotate.
- When the LAST job finishes, we only DISCONNECT (same as your original logic).
- Optional queuing: limit concurrent downloads via env YTPDL_MAX_PARALLEL (default 4).

Notes:
- This relies on a single Gunicorn worker process (-w 1) so that the module-level
  state is shared among requests. If you scale to multiple processes, you’ll want
  an inter-process lock (e.g., file lock) instead.
- Public function signature stays the same: download_video(url, resolution, extension, out_dir).
- If Mullvad isn’t installed, all VPN steps are no-ops (unchanged from before).

Goals (unchanged):
- Prefer exact 1080p H.264 (avc1) + AAC in MP4 (no re-encode).
- If that doesn't exist, exact 1080p in ANY codec/container (VP9/AV1/WebM/MKV/MP4).
- If 1080p truly doesn't exist, fall back to best <= 1080p.
- Audio-only (mp3) supported.

Env:
- YTPDL_VENV               (default: /opt/yt-dlp-mullvad/venv)
- YTPDL_MULLVAD_LOCATION   (default: "us")
- YTPDL_USER_AGENT         (override UA)
- YTPDL_MAX_PARALLEL       (default: 4)  # number of concurrent downloads; queued beyond this
"""

from __future__ import annotations
import os
import shlex
import shutil
import subprocess
import time
from typing import Optional, List
from threading import Lock, BoundedSemaphore

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
MAX_PARALLEL = int(os.environ.get("YTPDL_MAX_PARALLEL", "4"))

# =========================
# Concurrency state
# =========================
# Single-process coordination: one lock protects the active-jobs counter.
# A bounded semaphore provides lightweight queuing for parallelism throttling.
_state_lock = Lock()
_active_jobs = 0
_slots = BoundedSemaphore(MAX_PARALLEL)

# =========================
# Shell helpers
# =========================
def _run_argv(argv: List[str], check: bool = True) -> str:
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
    res = subprocess.run(["mullvad", "account", "get"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return "not logged in" not in (res.stdout or "").lower()

def manual_login(mullvad_account: str) -> None:
    if not _mullvad_present():
        raise RuntimeError("Mullvad CLI not installed on this host.")
    if not mullvad_account:
        raise RuntimeError("Missing Mullvad account number.")
    res = subprocess.run(["mullvad", "account", "get"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if "not logged in" not in (res.stdout or "").lower():
        print("Already logged into Mullvad.")
        return
    _run_argv(["mullvad", "account", "login", mullvad_account])
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
    # Rotate: disconnect first, then (optionally set relay) and connect.
    _run_argv(["mullvad", "disconnect"], check=False)
    if loc:
        _run_argv(["mullvad", "relay", "set", "location", loc], check=False)
    _run_argv(["mullvad", "connect"], check=False)

def mullvad_wait_connected(timeout: int = 10) -> bool:
    if not _mullvad_present():
        return True
    for _ in range(timeout):
        res = subprocess.run(["mullvad", "status"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if "Connected" in (res.stdout or ""):
            return True
        time.sleep(1)
    return False

# ---------- New: job lifecycle around Mullvad ----------
def _begin_job() -> None:
    """Increment active job count; if this is the first, rotate/connect Mullvad."""
    global _active_jobs
    first_job = False
    with _state_lock:
        first_job = (_active_jobs == 0)
        _active_jobs += 1

    if first_job:
        # Rotate at batch start (first job only)
        mullvad_connect(MULLVAD_LOCATION)
        if not mullvad_wait_connected():
            # If connect failed, roll back active count so others don't hang.
            with _state_lock:
                _active_jobs -= 1
            raise RuntimeError("Could not establish Mullvad VPN connection.")

def _end_job() -> None:
    """Decrement active job count; if this was the last, disconnect Mullvad."""
    global _active_jobs
    last_job = False
    with _state_lock:
        _active_jobs -= 1
        if _active_jobs < 0:
            _active_jobs = 0  # safety
        last_job = (_active_jobs == 0)

    if last_job and _mullvad_present():
        # Between batches we stay disconnected (same as your original behavior).
        _run_argv(["mullvad", "disconnect"], check=False)

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

def _common_flags_list() -> List[str]:
    return [
        "--retries", "6",
        "--fragment-retries", "6",
        "--retry-sleep", "2",
        "--user-agent", MODERN_UA,
        "--no-cache-dir",
        "--ignore-config",
        "--embed-metadata",
    ]

def _try_fmt(url: str, out_tpl: str, fmt: str, sort: Optional[str], merge_to_mp4: bool) -> Optional[str]:
    argv = [YTDLP_BIN, "-f", fmt]
    if sort:
        argv += ["-S", sort]
    argv += _common_flags_list()
    if merge_to_mp4:
        argv += ["--merge-output-format", "mp4"]
    argv += ["--output", out_tpl, url]

    out = _run_argv(argv, check=False)
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
        resolution: Target height cap; we try EXACT 1080p first, then best <=1080p.
        extension: "mp3" => extract audio; otherwise treat as video.
        out_dir: Target directory.

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

    # Queue limit for parallel downloads (optional)
    _slots.acquire()
    try:
        # Coordinate Mullvad rotation across concurrent jobs
        _begin_job()
        try:
            # ---------- Audio-only ----------
            if extension and extension.lower() == "mp3":
                out_tpl = os.path.join(out_dir, "%(title)s.%(ext)s")
                argv = [
                    YTDLP_BIN, "-x", "--audio-format", "mp3",
                    *(_common_flags_list()),
                    "--output", out_tpl, url
                ]
                out = _run_argv(argv, check=True)
                path = _extract_downloaded_filename(out)
                if not path or not os.path.exists(path):
                    raise RuntimeError("Audio download finished but file not found.")
                return os.path.abspath(path)

            # ---------- Video ----------
            cap = int(resolution or 1080)
            out_tpl = os.path.join(out_dir, "%(title)s.%(ext)s")

            # A) EXACT 1080p, H.264 (avc1) + AAC in MP4 (no re-encode merges)
            fmt_h264_1080 = (
                "bv*[height=1080][vcodec~='^(?:avc1|h264)'][ext=mp4]"
                "+ba[acodec~='^mp4a'][ext=m4a]/"
                "b[height=1080][vcodec~='^(?:avc1|h264)'][ext=mp4]"
            )
            sort_h264_1080 = "codec:h264,res,fps,br,filesize"
            path = _try_fmt(url, out_tpl, fmt_h264_1080, sort_h264_1080, merge_to_mp4=True)
            if path:
                return os.path.abspath(path)

            # B) EXACT 1080p, ANY codec/container (no forced MP4 merge)
            fmt_any_1080 = "bv*[height=1080]+ba/b[height=1080]"
            sort_any_1080 = "res,fps,br,filesize"
            path = _try_fmt(url, out_tpl, fmt_any_1080, sort_any_1080, merge_to_mp4=False)
            if path:
                return os.path.abspath(path)

            # C) If 1080p truly not present, take best <=1080p (ANY codec/container)
            fmt_best_upto = f"bv*[height<={cap}]+ba/b[height<={cap}]"
            sort_best_upto = "res,fps,br,filesize"
            path = _try_fmt(url, out_tpl, fmt_best_upto, sort_best_upto, merge_to_mp4=False)
            if not path or not os.path.exists(path):
                raise RuntimeError("Video download finished but file not found.")
            return os.path.abspath(path)

        finally:
            # Decrement active-jobs and (only if we’re the last) disconnect Mullvad
            _end_job()
    finally:
        # Release the queued slot
        try:
            _slots.release()
        except ValueError:
            pass
