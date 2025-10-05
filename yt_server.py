from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ✅ السماح للتطبيقات الخارجية (مثل Flutter) بالاتصال

# مجلد مؤقت لحفظ الملفات مؤقتاً
DOWNLOAD_DIR = tempfile.gettempdir()


@app.route("/")
def home():
    return jsonify({"status": "✅ Server is running!", "version": "2.0"})


@app.route("/info")
def info():
    """
    🔹 يجلب معلومات الفيديو (العنوان + الصورة المصغرة)
    """
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "❌ Missing URL"}), 400

    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get("title", "No Title")
            thumbnail = info_dict.get("thumbnail", "")
        return jsonify({"title": title, "thumbnail": thumbnail})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download")
def download():
    """
    🔹 تحميل الفيديو أو الصوت (MP4 / MP3)
    """
    url = request.args.get("url")
    file_type = request.args.get("type", "mp4")

    if not url:
        return jsonify({"error": "❌ Missing URL"}), 400

    try:
        out_file = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

        # إعدادات التحميل
        if file_type == "mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": out_file,
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
                ],
            }
        else:
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": out_file,
                "merge_output_format": "mp4",
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if file_type == "mp3":
                filename = filename.rsplit(".", 1)[0] + ".mp3"

        # ✅ إرسال الرابط أو الملف المباشر
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
