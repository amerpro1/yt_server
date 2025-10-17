from flask import Flask, request, jsonify
import yt_dlp, os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "✅ Server is running!"})

@app.route('/api/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    merge = request.args.get('merge')
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "forcejson": True,
        "extract_flat": False,
        "noplaylist": True,
        "format": "bestvideo+bestaudio/best" if merge else "bestvideo/best",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if not f.get("url"):
                continue

            acodec, vcodec = f.get("acodec") or "", f.get("vcodec") or ""
            ext = f.get("ext") or "mp4"
            is_audio = (vcodec == "none" or vcodec == "") and acodec != "none"
            is_video = vcodec != "none" and vcodec != ""

            if is_audio or is_video:
                quality = f.get("format_note") or f.get("resolution") or f.get("abr") or "unknown"
                formats.append({
                    "url": f.get("url"),
                    "ext": "mp3" if is_audio else "mp4",
                    "quality": quality,
                    "type": "audio" if is_audio else "video",
                })

        videos = sorted([f for f in formats if f["type"] == "video"], key=lambda x: x["quality"])[:5]
        audios = sorted([f for f in formats if f["type"] == "audio"], key=lambda x: x["quality"])[:5]

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "formats": videos + audios
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # ✅ دعم Render (المنفذ الديناميكي)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
