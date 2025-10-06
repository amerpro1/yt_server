# yt_server.py
from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import tempfile

app = Flask(__name__)

COOKIES_PATH = "youtube.com_cookies.txt"  # ملف الكوكيز من المتصفح (اختياري)

@app.route('/')
def home():
    return jsonify({
        "status": "✅ Universal Video Downloader Server is Running",
        "version": "4.0",
        "supported_sites": [
            "YouTube", "Facebook", "Instagram", "TikTok", "X (Twitter)", "Reels", "Pinterest"
        ]
    })

@app.route('/info')
def info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "❌ Missing URL"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'cookiefile': COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "extractor": info.get("extractor"),
                "webpage_url": info.get("webpage_url"),
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download')
def download():
    url = request.args.get("url")
    media_type = request.args.get("type", "mp4")  # mp3 or mp4
    if not url:
        return jsonify({"error": "❌ Missing URL"}), 400

    try:
        tmp_dir = tempfile.mkdtemp()
        out_path = os.path.join(tmp_dir, "%(title)s.%(ext)s")

        ydl_opts = {
            'outtmpl': out_path,
            'cookiefile': COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
            'format': 'bestaudio/best' if media_type == 'mp3' else 'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }] if media_type == 'mp3' else []
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if media_type == "mp3":
                file_path = os.path.splitext(file_path)[0] + ".mp3"

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
