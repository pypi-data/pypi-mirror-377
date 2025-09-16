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
    try:
        result = subprocess.run(
            cmd, shell=True, check=check,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {cmd}\n{e.output.strip()}") from e


# =========================
# Environment / Mullvad
# =========================
def get_venv_path():
    return "/opt/yt-dlp-mullvad/venv"

def validate_environment():
    """Strict venv validation (matches your original behavior)."""
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
    filename = None
    for line in output.splitlines():
        if line.startswith("[download]"):
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
    cmd = f"ffprobe -v error -print_format json -show_streams -select_streams v:0,a:0 {shlex.quote(path)}"
    out = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout
    try:
        return json.loads(out).get("streams", [])
    except Exception:
        return []

def _is_ios_safe_mp4(path):
    """
    iOS/macOS-safe = MP4/M4V + H.264 (8-bit, yuv420p), profile {Baseline/Main/High}, level <= 4.2,
                     <=1080p frame size, AAC/MP3/ALAC audio (<=48kHz, <=2ch).
    Conservative to ensure Photos/Files/Quick Look playback.
    """
    streams = _ffprobe_streams(path)
    if not streams:
        return False

    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    _, ext = os.path.splitext(path)
    if ext.lower() not in (".mp4", ".m4v"):
        return False

    # ---- video checks ----
    if not v or v.get("codec_name") not in ("h264", "avc1"):
        return False

    # Pixel format must be 4:2:0 8-bit
    if v.get("pix_fmt") not in ("yuv420p", "nv12", "yuvj420p"):
        return False
    bpr = v.get("bits_per_raw_sample")
    if bpr and str(bpr).isdigit() and int(bpr) > 8:
        return False

    # Profile & level (ffprobe 'level' is e.g. 42 for 4.2)
    profile = (v.get("profile") or "").lower()
    if profile and not any(p in profile for p in ("baseline", "main", "high")):
        return False
    level = v.get("level")
    if isinstance(level, int) and level > 42:
        return False

    # Resolution cap
    w, h = (v.get("width") or 0), (v.get("height") or 0)
    if w > 1920 or h > 1080:
        return False

    # ---- audio checks ----
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

def _transcode_to_ios_mp4(src_path):
    """
    Force Apple-compat:
      - H.264 High@4.2, yuv420p (8-bit), <=1080p (keeps AR, never upscales)
      - AAC LC, 48 kHz, stereo
      - moov at head for instant start
    """
    base, _ = os.path.splitext(src_path)
    dst_path = base + ".ios.mp4"

    # Cap to 1080p while preserving aspect ratio; don’t upscale.
    vf = "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease"

    cmd = (
        "ffmpeg -y -i {src} "
        "-map 0:v:0 -map 0:a:0? "
        f"-vf {vf} "
        "-c:v libx264 -profile:v high -level 4.2 -pix_fmt yuv420p -preset veryfast -crf 20 "
        "-c:a aac -b:a 160k -ar 48000 -ac 2 "
        "-movflags +faststart "
        "-map_metadata 0 "
        "{dst}"
    ).format(src=shlex.quote(src_path), dst=shlex.quote(dst_path))

    subprocess.run(cmd, shell=True, check=True)
    return dst_path


# =========================
# yt-dlp flags
# =========================
MODERN_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# NEW: region pin (override with env)
MULLVAD_LOCATION = os.environ.get("YTPDL_MULLVAD_LOCATION", "us")

def _common_flags_desktop():
    # Desktop: codec-agnostic; ask as web client; allow dual-stack
    return (
        "--retries 6 --fragment-retries 6 --retry-sleep 2 "
        f"--user-agent '{MODERN_UA}' "
        "--no-cache-dir --ignore-config "
    )

def _common_flags_apple():
    # Apple/mobile: keep your existing behavior (android+web hint, IPv4)
    return (
        "--force-ipv4 "
        "--retries 6 --fragment-retries 6 --retry-sleep 2 "
        "--extractor-args \"youtube:player_client=android,web\" "
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
            # eligible to try the next plan
            raise ValueError(str(e))
        raise


# =========================
# Public API
# =========================
def download_video(url, resolution=None, extension=None, prefer_avc1=False):
    """
    Apple/mobile (prefer_avc1=True):
        1) Native 1080p H.264/AAC MP4 (DASH or progressive).
        2) If not available, download best <=1080 (any codec/container) and transcode to MP4/H.264/AAC.
        3) If (2) fails, try native 720p H.264/AAC MP4; if that fails, download best <=720 and transcode.
    Desktop (prefer_avc1=False):
        Best <=1080 (any codec/container). No MP4 forcing.
    """
    venv_path = validate_environment()
    check_mullvad()
    require_logged_in()

    # Stable relay per env (avoid random exits that hide 1080p)
    run_command("mullvad disconnect", check=False)
    run_command(f"mullvad relay set location {shlex.quote(MULLVAD_LOCATION)}", check=False)

    print("Connecting to Mullvad VPN...")
    run_command("mullvad connect")
    if not wait_for_connection():
        raise RuntimeError("Could not establish Mullvad VPN connection.")

    print(f"Downloading: {url}")
    common = _common_flags_apple() if prefer_avc1 else _common_flags_desktop()
    cap = int(resolution or 1080)
    out_tpl = "--output '/root/%(title)s.%(ext)s'"

    try:
        # ---------- Audio-only ----------
        audio_exts = {"mp3", "m4a", "aac", "wav", "flac", "opus", "ogg"}
        if extension and extension.lower() in audio_exts:
            ytdlp_cmd = (
                f"{venv_path}/bin/yt-dlp -x --audio-format {extension} "
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

        # ---------- Video ----------
        if prefer_avc1:
            # (1) Native 1080p H.264/AAC MP4 (DASH first, then progressive)
            fmt_1080_dash = "bv*[ext=mp4][vcodec^=avc1][height=1080]+ba[ext=m4a][acodec^=mp4a]"
            fmt_1080_prog = "b[ext=mp4][vcodec^=avc1][height=1080]"
            sort_h264 = '-S "codec:h264:m4a,ext:mp4,res,filesize"'
            output = None

            try:
                y1 = (
                    f"{venv_path}/bin/yt-dlp -f \"{fmt_1080_dash}\" {sort_h264} "
                    f"{common} --remux-video mp4 --embed-metadata "
                    f"--postprocessor-args \"ffmpeg:-movflags +faststart\" "
                    f"{out_tpl} {url}"
                )
                output = _try_run(y1)
            except ValueError:
                try:
                    y2 = (
                        f"{venv_path}/bin/yt-dlp -f \"{fmt_1080_prog}\" {sort_h264} "
                        f"{common} --embed-metadata "
                        f"--postprocessor-args \"ffmpeg:-movflags +faststart\" "
                        f"{out_tpl} {url}"
                    )
                    output = _try_run(y2)
                except ValueError:
                    output = None

            filename = _extract_downloaded_filename(output or "")
            if filename and os.path.exists(filename):
                if not _is_ios_safe_mp4(filename):
                    filename = _transcode_to_ios_mp4(filename)
                print(f"DOWNLOADED_FILE:{filename}")
                return filename

            # (2) No native 1080p H.264: best <=1080 ANY codec -> transcode
            fmt_best_1080_any = f"bv*[height<={cap}]+ba/b[height<={cap}]"
            try:
                y_any_1080 = (
                    f"{venv_path}/bin/yt-dlp -f \"{fmt_best_1080_any}\" "
                    f"{common} --embed-metadata "
                    f"{out_tpl} {url}"
                )
                output = _try_run(y_any_1080)
                filename = _extract_downloaded_filename(output)
                if filename and os.path.exists(filename):
                    if not _is_ios_safe_mp4(filename):
                        print("No native 1080p H.264; transcoding best<=1080 to MP4/H.264…")
                        filename = _transcode_to_ios_mp4(filename)
                    print(f"DOWNLOADED_FILE:{filename}")
                    return filename
            except ValueError:
                pass  # move to (3)

            # (3) Try native 720p H.264 MP4; else best <=720 ANY -> transcode
            fmt_720_dash = "bv*[ext=mp4][vcodec^=avc1][height=720]+ba[ext=m4a][acodec^=mp4a]"
            fmt_720_prog = "b[ext=mp4][vcodec^=avc1][height=720]"
            output = None
            try:
                y3 = (
                    f"{venv_path}/bin/yt-dlp -f \"{fmt_720_dash}\" {sort_h264} "
                    f"{common} --remux-video mp4 --embed-metadata "
                    f"--postprocessor-args \"ffmpeg:-movflags +faststart\" "
                    f"{out_tpl} {url}"
                )
                output = _try_run(y3)
            except ValueError:
                try:
                    y4 = (
                        f"{venv_path}/bin/yt-dlp -f \"{fmt_720_prog}\" {sort_h264} "
                        f"{common} --embed-metadata "
                        f"--postprocessor-args \"ffmpeg:-movflags +faststart\" "
                        f"{out_tpl} {url}"
                    )
                    output = _try_run(y4)
                except ValueError:
                    output = None

            filename = _extract_downloaded_filename(output or ""
            )
            if filename and os.path.exists(filename):
                if not _is_ios_safe_mp4(filename):
                    filename = _transcode_to_ios_mp4(filename)
                print(f"DOWNLOADED_FILE:{filename}")
                return filename

            # Last-resort: <=720 any -> transcode
            fmt_best_720_any = "bv*[height<=720]+ba/b[height<=720]"
            y_any_720 = (
                f"{venv_path}/bin/yt-dlp -f \"{fmt_best_720_any}\" "
                f"{common} --embed-metadata "
                f"{out_tpl} {url}"
            )
            output = run_command(y_any_720)
            filename = _extract_downloaded_filename(output)
            if filename and os.path.exists(filename):
                if not _is_ios_safe_mp4(filename):
                    filename = _transcode_to_ios_mp4(filename)
                print(f"DOWNLOADED_FILE:{filename}")
                return filename

            print("Download failed: File not found")
            return None

        else:
            # Desktop: best <=1080 (any codec/container). No MP4 forcing.
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
        # Let api.py surface the error text
        raise
    finally:
        print("Disconnecting VPN...")
        run_command("mullvad disconnect", check=False)
