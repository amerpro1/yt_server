from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import tempfile
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ⚙️ إعدادات عامة
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "cookies.txt")
RAPID_API_KEY = "177531b8e2mshca7e034984ce5bbp1a0046jsnff3ed7629b4d"
RAPID_API_HOST = "all-video-downloader1.p.rapidapi.com"

@app.route("/")
def home():
    return jsonify({
        "status": "✅ Server is running!",
        "version": "4.0",
        "mode": "yt-dlp + RapidAPI Hybrid",
        "supports": "YouTube, TikTok, Instagram, Facebook, Twitter, Likee, Vimeo, Pinterest"
    })

# ✅ 1. جلب معلومات الفيديو
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
        print(f"[yt-dlp error] {str(e)}")
        # 🧠 محاولة جلب المعلومات من RapidAPI كبديل
        try:
            headers = {
                "x-rapidapi-key": RAPID_API_KEY,
                "x-rapidapi-host": RAPID_API_HOST,
            }
            res = requests.get(f"https://{RAPID_API_HOST}/", params={"url": url}, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return jsonify({
                    "title": data.get("title", "فيديو بدون عنوان"),
                    "thumbnail": data.get("thumbnail"),
                    "duration": data.get("duration"),
                    "url": data.get("url"),
                    "source": "rapidapi"
                })
            else:
                return jsonify({"error": "⚠️ لا يمكن جلب المعلومات."}), 500
        except Exception as ex:
            return jsonify({"error": f"❌ فشل جلب البيانات: {str(ex)}"}), 500

# ✅ 2. تحميل الفيديو أو الصوت
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
        print(f"[yt-dlp download failed] {str(e)}")
        # ⚙️ التحول إلى RapidAPI في حال فشل yt-dlp
        try:
            headers = {
                "x-rapidapi-key": RAPID_API_KEY,
                "x-rapidapi-host": RAPID_API_HOST,
            }
            res = requests.get(f"https://{RAPID_API_HOST}/", params={"url": url}, headers=headers)
            if res.status_code == 200:
                data = res.json()
                alt_url = data.get("url")
                if not alt_url:
                    return jsonify({"error": "⚠️ RapidAPI لم يُرجع رابط تحميل"}), 500

                # تحميل الملف من RapidAPI URL
                with requests.get(alt_url, stream=True) as r:
                    with open(file_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                return send_file(file_path, as_attachment=True)
            else:
                return jsonify({"error": "⚠️ RapidAPI download failed"}), 500
        except Exception as ex:
            return jsonify({"error": f"❌ Fallback error: {str(ex)}"}), 500
    finally:
        try:
            os.remove(file_path)
        except:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server running on port {port}")
    app.run(host="0.0.0.0", port=port)
