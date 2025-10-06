from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# مسار ملف الكوكيز (اختياري)
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "cookies.txt")

@app.route("/")
def home():
    return jsonify({"status": "✅ Server is running!", "version": "3.0", "supports": "YouTube, TikTok, Instagram, Facebook, Twitter"})

# ✅ جلب معلومات الفيديو
@app.route("/info", methods=["GET"])
def get_info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "❌ Missing URL"}), 400

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "cookies": COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get("title", "بدون عنوان"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "ext": info.get("ext"),
                "webpage_url": info.get("webpage_url"),
            })
    except Exception as e:
        return jsonify({"error": f"⚠️ Error: {str(e)}"}), 500

# ✅ تحميل الفيديو أو الصوت
@app.route("/download", methods=["GET"])
def download_video():
    url = request.args.get("url")
    media_type = request.args.get("type", "mp4")

    if not url:
        return jsonify({"error": "❌ Missing URL"}), 400

    temp_dir = tempfile.mkdtemp()
    filename = f"downloaded_media.{media_type}"
    file_path = os.path.join(temp_dir, filename)

    ydl_opts = {
        "outtmpl": file_path,
        "format": "bestaudio/best" if media_type == "mp3" else "bestvideo+bestaudio/best",
        "merge_output_format": media_type,
        "noplaylist": True,
        "cookies": COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"⚠️ Download failed: {str(e)}"}), 500
    finally:
        try:
            os.remove(file_path)
        except:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server started on port {port}")
    app.run(host="0.0.0.0", port=port)
