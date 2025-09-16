#!/usr/bin/env python3
import subprocess
import os
import time
import shutil
import json
import shlex

# =========================
# Shell helpers
# =========================
def run_command(cmd, check=True):
    """Shell runner for yt-dlp only (we control quoting there)."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=check,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {cmd}\n{e.output.strip()}") from e

def run_argv(argv, check=True):
    """Arg-list runner (safe for ffmpeg/ffprobe with quotes/emoji in filenames)."""
    try:
        result = subprocess.run(
            argv, check=check,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        cmd = " ".join(shlex.quote(p) for p in argv)
        raise RuntimeError(f"Command failed: {cmd}\n{e.stdout.strip()}") from e


# =========================
# Environment / Mullvad
# =========================
def get_venv_path():
    return "/opt/yt-dlp-mullvad/venv"

def validate_environment():
    venv_path = get_venv_path()
    current_venv = os.environ.get("VIRTUAL_ENV")
    if not current_venv or current_venv != venv_path:
        raise RuntimeError(
            "This package must run from the virtual environment at "
            f"{venv_path}\nCurrent VIRTUAL_ENV: {current_venv}\n\n"
            "To fix:\n"
            f"  1) python3 -m venv {venv_path}\n"
            f"  2) source {venv_path}/bin/activate\n"
            "  3) pip install ytp-dl"
        )
    ytdlp_path = f"{venv_path}/bin/yt-dlp"
    if not os.path.exists(ytdlp_path):
        raise RuntimeError(f"yt-dlp not found at {ytdlp_path}. Reinstall the package inside the venv.")
    return venv_path

def check_mullvad():
    if not shutil.which("mullvad"):
        raise RuntimeError(
            "Mullvad CLI not found.\n"
            "Install:\n"
            "  curl -fsSLo /tmp/mullvad.deb https://mullvad.net/download/app/deb/latest/\n"
            "  sudo apt install -y /tmp/mullvad.deb"
        )

def is_logged_in() -> bool:
    out = run_command("mullvad account get", check=False) or ""
    return "not logged in" not in out.lower()

def manual_login(mullvad_account: str):
    if not mullvad_account:
        raise RuntimeError("Missing Mullvad account for manual login.")
    if is_logged_in():
        print("Already logged into Mullvad on this server.")
        return
    print("Logging into Mullvad (one-time)…")
    run_command(f"mullvad account login {mullvad_account}")
    print("Login complete. No VPN connection was started.")

def require_logged_in():
    if not is_logged_in():
        raise RuntimeError(
            "Mullvad is not logged in on this server. "
            "SSH in and run: mullvad account login <ACCOUNT> (one-time)."
        )

def wait_for_connection(timeout=10):
    for _ in range(timeout):
        status = run_command("mullvad status", check=False) or ""
        if "Connected" in status:
            print("Mullvad VPN connected.")
            return True
        time.sleep(1)
    print("Failed to confirm Mullvad VPN connection within timeout.")
    return False


# =========================
# Filename & probe helpers
# =========================
def _extract_downloaded_filename(output: str):
    """
    Parse yt-dlp stdout to find the destination filename.
    Handles both fresh downloads and "already downloaded".
    """
    filename = None
    for line in output.splitlines():
        if not line.startswith("[download]"):
            continue
        if "Destination:" in line:
            filename = line.split("Destination: ")[1].strip()
        elif "has already been downloaded" in line:
            start = line.find("] ") + 2
            end = line.find(" has already been downloaded")
            filename = line[start:end].strip()
        if filename and filename.startswith("'") and filename.endswith("'"):
            filename = filename[1:-1]
        if filename:
            break
    return filename

def _ffprobe_streams(path):
    argv = [
        "ffprobe", "-v", "error",
        "-print_format", "json",
        "-show_streams", "-select_streams", "v:0,a:0",
        path
    ]
    out = run_argv(argv, check=False)
    try:
        return json.loads(out).get("streams", [])
    except Exception:
        return []

def _is_apple_safe_mp4(path):
    """
    Apple-safe playback (iOS/macOS Photos/Files/Quick Look):
      - Container: .mp4/.m4v
      - Video: H.264/AVC (8-bit yuv420p), Baseline/Main/High, level <= 4.2, <=1080p
      - Audio: AAC/MP4A/ALAC/MP3, <=48kHz, <=2ch
    """
    streams = _ffprobe_streams(path)
    if not streams:
        return False

    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    _, ext = os.path.splitext(path)
    if ext.lower() not in (".mp4", ".m4v"):
        return False

    # Video checks
    if not v or v.get("codec_name") not in ("h264", "avc1"):
        return False
    if v.get("pix_fmt") not in ("yuv420p", "nv12", "yuvj420p"):
        return False
    bpr = v.get("bits_per_raw_sample")
    if bpr and str(bpr).isdigit() and int(bpr) > 8:
        return False
    profile = (v.get("profile") or "").lower()
    if profile and not any(p in profile for p in ("baseline", "main", "high")):
        return False
    level = v.get("level")
    if isinstance(level, int) and level > 42:
        return False
    w, h = (v.get("width") or 0), (v.get("height") or 0)
    if w > 1920 or h > 1080:
        return False

    # Audio checks
    if a:
        if a.get("codec_name") not in ("aac", "mp4a", "alac", "mp3"):
            return False
        ch = a.get("channels")
        if isinstance(ch, int) and ch > 2:
            return False
        sr = a.get("sample_rate")
        try:
            if sr and int(sr) > 48000:
                return False
        except Exception:
            pass

    return True

def _transcode_to_apple_compatible_mp4(src_path):
    """
    Transcode to an Apple-compatible MP4:
      - H.264 High@4.2, yuv420p (8-bit), <=1080p (keep AR, don't upscale)
      - AAC LC, 48 kHz, stereo
      - moov at head (+faststart)
    """
    base, _ = os.path.splitext(src_path)
    dst_path = base + ".ios.mp4"

    vf_expr = "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease"

    argv = [
        "ffmpeg", "-y",
        "-i", src_path,
        "-map", "0:v:0", "-map", "0:a:0?",
        "-vf", vf_expr,
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
        "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart",
        "-map_metadata", "0",
        dst_path
    ]
    run_argv(argv, check=True)
    return dst_path


# =========================
# yt-dlp flags & helpers
# =========================
MODERN_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Region pin (override with env). Helps avoid exits where 1080p is missing.
MULLVAD_LOCATION = os.environ.get("YTPDL_MULLVAD_LOCATION", "us")

def _common_flags_desktop():
    return (
        "--retries 6 --fragment-retries 6 --retry-sleep 2 "
        f"--user-agent '{MODERN_UA}' "
        "--no-cache-dir --ignore-config "
    )

def _common_flags_apple():
    # Use web-only client hint to maximize format availability
    return (
        "--retries 6 --fragment-retries 6 --retry-sleep 2 "
        "--extractor-args \"youtube:player_client=web\" "
        f"--user-agent '{MODERN_UA}' "
        "--no-cache-dir --ignore-config "
    )

def _try_run(cmd):
    try:
        return run_command(cmd)
    except RuntimeError as e:
        low = str(e).lower()
        if ("requested format is not available" in low
            or "no such format" in low
            or "unable to download video data" in low
            or "this video is only available in certain formats" in low):
            raise ValueError(str(e))
        raise


# =========================
# Public API
# =========================
def download_video(url, resolution=None, extension=None, prefer_avc1=False):
    """
    Apple/mobile (prefer_avc1=True):
        A) Try best H.264 <=1080 using desktop flags (more formats visible).
        B) Fall back to best <=1080 any codec -> transcode if needed.
        C) Final fallback to <=720.
    Desktop (prefer_avc1=False):
        Best <=1080 any codec/container (no re-encode).
    """
    venv_path = validate_environment()
    check_mullvad()
    require_logged_in()

    # Keep a stable relay to avoid "no 1080p in this exit" cases.
    run_command("mullvad disconnect", check=False)
    run_command(f"mullvad relay set location {shlex.quote(MULLVAD_LOCATION)}", check=False)

    print("Connecting to Mullvad VPN...")
    run_command("mullvad connect")
    if not wait_for_connection():
        raise RuntimeError("Could not establish Mullvad VPN connection.")

    print(f"Downloading: {url}")
    cap = int(resolution or 1080)
    out_tpl = "--output '/root/%(title)s.%(ext)s'"

    try:
        # ---------- Audio-only ----------
        audio_exts = {"mp3", "m4a", "aac", "wav", "flac", "opus", "ogg"}
        if extension and extension.lower() in audio_exts:
            common_audio = _common_flags_desktop()
            ytdlp_cmd = (
                f"{venv_path}/bin/yt-dlp -x --audio-format {extension} "
                f"{common_audio} --embed-metadata "
                f"{out_tpl} {url}"
            )
            output = run_command(ytdlp_cmd)
            filename = _extract_downloaded_filename(output)
            if filename and os.path.exists(filename):
                print(f"DOWNLOADED_FILE:{filename}")
                return filename
            print("Download failed: File not found")
            return None

        # ---------- Video ----------
        if prefer_avc1:
            # FIXED: Use desktop flags for ALL attempts to ensure 1080p formats are visible
            # Only use web client (not android) to maximize format availability
            common_any = _common_flags_desktop()
            sort_by_res = '-S "res:1080,fps,br,filesize"'
            
            # A) Try to get native H.264 <=1080 (best quality, no transcoding needed)
            fmt_h264_1080 = f"bv*[vcodec~='^avc1'][height<={cap}]+ba[acodec~='^mp4a']/b[vcodec~='^avc1'][height<={cap}]"
            try:
                y_h264 = (
                    f"{venv_path}/bin/yt-dlp -f \"{fmt_h264_1080}\" {sort_by_res} "
                    f"{common_any} --merge-output-format mp4 --embed-metadata "
                    f"--postprocessor-args \"ffmpeg:-movflags +faststart\" "
                    f"{out_tpl} {url}"
                )
                output = _try_run(y_h264)
                filename = _extract_downloaded_filename(output)
                if filename and os.path.exists(filename):
                    if not _is_apple_safe_mp4(filename):
                        filename = _transcode_to_apple_compatible_mp4(filename)
                    print(f"DOWNLOADED_FILE:{filename}")
                    return filename
            except ValueError:
                print("No native H.264 ≤1080p found, trying any codec...")

            # B) Any codec ≤1080 -> transcode if needed
            fmt_any_1080 = f"bv*[height<={cap}]+ba/b[height<={cap}]"
            try:
                y_any_1080 = (
                    f"{venv_path}/bin/yt-dlp -f \"{fmt_any_1080}\" {sort_by_res} "
                    f"{common_any} --embed-metadata "
                    f"{out_tpl} {url}"
                )
                output = _try_run(y_any_1080)
                filename = _extract_downloaded_filename(output)
                if filename and os.path.exists(filename):
                    if not _is_apple_safe_mp4(filename):
                        print("Transcoding ≤1080p to Apple-compatible MP4...")
                        filename = _transcode_to_apple_compatible_mp4(filename)
                    print(f"DOWNLOADED_FILE:{filename}")
                    return filename
            except ValueError:
                print("No ≤1080p found, trying ≤720p...")

            # C) Fallback to ≤720
            cap_720 = 720
            sort_720 = '-S "res:720,fps,br,filesize"'
            
            # Try H.264 ≤720 first
            fmt_h264_720 = f"bv*[vcodec~='^avc1'][height<={cap_720}]+ba[acodec~='^mp4a']/b[vcodec~='^avc1'][height<={cap_720}]"
            try:
                y_h264_720 = (
                    f"{venv_path}/bin/yt-dlp -f \"{fmt_h264_720}\" {sort_720} "
                    f"{common_any} --merge-output-format mp4 --embed-metadata "
                    f"--postprocessor-args \"ffmpeg:-movflags +faststart\" "
                    f"{out_tpl} {url}"
                )
                output = _try_run(y_h264_720)
                filename = _extract_downloaded_filename(output)
                if filename and os.path.exists(filename):
                    if not _is_apple_safe_mp4(filename):
                        filename = _transcode_to_apple_compatible_mp4(filename)
                    print(f"DOWNLOADED_FILE:{filename}")
                    return filename
            except ValueError:
                pass

            # Last resort: any codec ≤720 -> transcode
            fmt_any_720 = f"bv*[height<={cap_720}]+ba/b[height<={cap_720}]"
            output = run_command(
                f"{venv_path}/bin/yt-dlp -f \"{fmt_any_720}\" {sort_720} "
                f"{common_any} --embed-metadata "
                f"{out_tpl} {url}"
            )
            filename = _extract_downloaded_filename(output)
            if filename and os.path.exists(filename):
                if not _is_apple_safe_mp4(filename):
                    filename = _transcode_to_apple_compatible_mp4(filename)
                print(f"DOWNLOADED_FILE:{filename}")
                return filename

            print("Download failed: File not found")
            return None

        else:
            # Desktop: best ≤1080 any codec/container
            common = _common_flags_desktop()
            fmt = f"bv*[height<={cap}]+ba/b[height<={cap}]"
            sort_desktop = '-S "res,fps,br,filesize"'
            ytdlp_cmd = (
                f"{venv_path}/bin/yt-dlp -f \"{fmt}\" {sort_desktop} "
                f"{common} --embed-metadata "
                f"{out_tpl} {url}"
            )
            output = run_command(ytdlp_cmd)
            filename = _extract_downloaded_filename(output)
            if filename and os.path.exists(filename):
                print(f"DOWNLOADED_FILE:{filename}")
                return filename
            print("Download failed: File not found")
            return None

    except Exception:
        raise
    finally:
        print("Disconnecting VPN...")
        run_command("mullvad disconnect", check=False)