from flask import Flask, request, jsonify, send_file
import requests
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "✅ Server is running!", "version": "4.0-lite"})

@app.route('/info')
def info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "❌ URL is required"}), 400
    try:
        # نستخدم واجهة savefrom API لجلب معلومات الفيديو
        r = requests.get(f"https://api.sssapi.app/api/v2/info?url={url}")
        data = r.json()
        if "meta" in data:
            return jsonify({
                "title": data["meta"].get("title", "No title"),
                "thumbnail": data["meta"].get("thumbnail", ""),
                "duration": data["meta"].get("duration", 0)
            })
        return jsonify({"error": "فشل في جلب المعلومات"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/download')
def download():
    url = request.args.get('url')
    dtype = request.args.get('type', 'mp4')

    if not url:
        return jsonify({"error": "❌ URL required"}), 400

    try:
        # استخدام API جاهز للتحميل من YouTube بدون yt_dlp
        api = f"https://api.sssapi.app/api/v2/convert?url={url}&format={dtype}"
        r = requests.get(api)
        j = r.json()

        # نحصل على رابط مباشر للتحميل
        if "url" in j:
            file_link = j["url"]

            # نحمل الملف مؤقتًا في السيرفر
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"video.{dtype}")

            with open(file_path, "wb") as f:
                f.write(requests.get(file_link).content)

            return send_file(file_path, as_attachment=True)

        return jsonify({"error": "❌ Download link not found"}), 500

    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
