import os
from flask import Flask, request, jsonify, send_file
import yt_dlp
import tempfile

app = Flask(__name__)

# ✅ مجلد مؤقت لحفظ الملفات
DOWNLOAD_DIR = tempfile.gettempdir()

# ✅ إعدادات yt-dlp العامة
def get_ydl_opts(audio_only=False):
    return {
        "quiet": True,
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "cookiefile": "cookies.txt",  # ⚙️ ملف الكوكيز (اختياري لكن مهم لليوتيوب)
        "format": "bestaudio/best" if audio_only else "best",
        "noplaylist": True,
        "ignoreerrors": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
    }

# ✅ فحص حالة السيرفر
@app.route("/")
def index():
    return jsonify({"status": "✅ Server is running!", "version": "2.5", "platforms": ["YouTube", "TikTok", "Instagram", "Facebook", "Twitter", "Direct links"]})


# ✅ جلب معلومات الفيديو
@app.route("/info")
def get_info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "❌ No URL provided"}), 400

    try:
        ydl_opts = get_ydl_opts()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "uploader": info.get("uploader"),
                "ext": info.get("ext"),
                "webpage_url": info.get("webpage_url"),
            })
    except Exception as e:
        return jsonify({"error": f"⚠️ Error fetching video info: {str(e)}"}), 500


# ✅ تحميل الفيديو أو الصوت
@app.route("/download")
def download_video():
    url = request.args.get("url")
    vtype = request.args.get("type", "mp4")

    if not url:
        return jsonify({"error": "❌ No URL provided"}), 400

    audio_only = (vtype == "mp3")
    try:
        ydl_opts = get_ydl_opts(audio_only)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"⚠️ Error downloading: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
