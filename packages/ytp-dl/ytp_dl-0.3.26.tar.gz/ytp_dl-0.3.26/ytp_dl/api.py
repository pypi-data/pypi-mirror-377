#!/usr/bin/env python3
"""
VPS downloader service (download-only; no transcoding).

POST /api/download
JSON: { "url": "<video or audio url>", "resolution": 1080, "extension": "mp4|mp3|..." }

Behavior:
- (Optionally) connects Mullvad if logged in, pinned to a region.
- Uses yt-dlp to prefer 1080p H.264/AAC MP4 when available, else falls back to best <=1080 any codec.
- Streams the completed file with proper headers:
  - Content-Disposition: attachment; filename="..."
  - Content-Length: <size>
  - X-Media-Info: {"ext","width","height","vcodec","acodec"}  <-- NEW for UI hints
"""
import os
import shlex
import shutil
import subprocess
import time
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

OUTPUT_DIR = os.environ.get("YTPDL_OUTPUT_DIR", "/root")
VENV_PATH  = os.environ.get("YTPDL_VENV", "/opt/yt-dlp-mullvad/venv")
YTDLP      = os.path.join(VENV_PATH, "bin", "yt-dlp")
MULLVAD_LOC= os.environ.get("YTPDL_MULLVAD_LOCATION", "us")

MODERN_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

app = Flask(__name__)
CORS(app)

# ---------- helpers ----------
def run_cmd(cmd: str) -> str:
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{res.stdout}")
    return res.stdout

def _ensure_paths():
    if not os.path.exists(YTDLP):
        raise RuntimeError(f"yt-dlp not found at {YTDLP}. Install it in the venv.")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def _mullvad_logged_in() -> bool:
    if shutil.which("mullvad") is None:
        return False
    out = subprocess.run(["mullvad", "account", "get"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return "not logged in" not in (out.stdout or "").lower()

def _mullvad_connect():
    if shutil.which("mullvad") is None:
        return
    subprocess.run(["mullvad", "disconnect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["mullvad", "relay", "set", "location", MULLVAD_LOC], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["mullvad", "connect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def _wait_connected(timeout=10):
    if shutil.which("mullvad") is None:
        return
    for _ in range(timeout):
        out = subprocess.run(["mullvad", "status"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if "Connected" in (out.stdout or ""):
            return
        time.sleep(1)

def _parse_ytdlp_dest(stdout: str) -> str | None:
    name = None
    for line in (stdout or "").splitlines():
        if line.startswith("[download] Destination: "):
            name = line.split("Destination: ", 1)[1].strip()
        elif "] " in line and " has already been downloaded" in line:
            start = line.find("] ")+2
            end = line.rfind(" has already been downloaded")
            name = line[start:end].strip().strip("'")
        if name:
            break
    return name

def _probe_basic_media_info(path: str):
    """Return {"ext","width","height","vcodec","acodec"} (best-effort; empty on failure)."""
    try:
        out = subprocess.check_output(
            ["ffprobe","-v","error","-print_format","json","-show_streams", path],
            text=True
        )
        data = json.loads(out)
        v = next((s for s in data.get("streams", []) if s.get("codec_type")=="video"), None)
        a = next((s for s in data.get("streams", []) if s.get("codec_type")=="audio"), None)
        info = {
            "ext": os.path.splitext(path)[1].lstrip("."),
            "width": v.get("width") if v else None,
            "height": v.get("height") if v else None,
            "vcodec": v.get("codec_name") if v else None,
            "acodec": a.get("codec_name") if a else None,
        }
        return info
    except Exception:
        return {}

# ---------- routes ----------
@app.route("/api/health", methods=["GET"])
def health():
    try:
        _ensure_paths()
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/download", methods=["POST"])
def api_download():
    """Downloads to disk first, then streams the finished file (with length + X-Media-Info)."""
    try:
        _ensure_paths()
        payload = request.get_json(force=True, silent=False) or {}
        url = payload.get("url")
        cap = int(payload.get("resolution") or 1080)
        extension = (payload.get("extension") or "mp4").lower()

        if not url:
            return jsonify({"error": "Missing url"}), 400

        # Connect VPN (optional)
        if _mullvad_logged_in():
            _mullvad_connect()
            _wait_connected()

        out_tpl = os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s")

        # Primary: prefer H.264/AAC MP4 at <=1080p; fallback to best <=1080 any codec
        fmt_chain = (
            "bv*[vcodec~='^(avc1|h264)'][ext=mp4][height<={cap}]"
            "+ba[acodec~='^(mp4a|aac)']/"
            "b[vcodec~='^(avc1|h264)'][ext=mp4][height<={cap}]/"
            "bv*[height<={cap}]+ba/"
            "b[height<={cap}]"
        ).format(cap=cap)

        sort = "-S res:1080,fps,br,filesize"
        # --merge-output-format mp4 keeps MP4 container when we need to merge streams
        common = (
            f"--retries 6 --fragment-retries 6 --retry-sleep 2 "
            f"--user-agent '{MODERN_UA}' "
            f"--no-cache-dir --ignore-config --embed-metadata "
            f"--merge-output-format mp4"
        )
        cmd = f"{shlex.quote(YTDLP)} -f \"{fmt_chain}\" {sort} {common} --output {shlex.quote(out_tpl)} {shlex.quote(url)}"

        stdout = run_cmd(cmd)
        filepath = _parse_ytdlp_dest(stdout)
        if not filepath or not os.path.exists(filepath):
            return jsonify({"error": "Download finished but file not found."}), 500

        size = os.path.getsize(filepath)
        resp = send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        resp.headers["Content-Length"] = str(size)

        # Attach basic media info for UI to display as an [info] line
        info = _probe_basic_media_info(filepath)
        if info:
            resp.headers["X-Media-Info"] = json.dumps(info)

        return resp
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
