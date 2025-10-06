from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "✅ Server is running!", "version": "3.5"})

@app.route('/info')
def info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "❌ URL is required"}), 400

    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "nocheckcertificate": True,
            "ignoreerrors": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get("title", "No title"),
                "thumbnail": info.get("thumbnail", ""),
                "uploader": info.get("uploader", ""),
                "duration": info.get("duration", 0)
            })
    except Exception as e:
        return jsonify({"error": f"Server processing error: {str(e)}"}), 500


@app.route('/download')
def download():
    url = request.args.get('url')
    dtype = request.args.get('type', 'mp4')

    if not url:
        return jsonify({"error": "❌ URL required"}), 400

    try:
        temp_dir = os.path.join(os.getcwd(), "downloads")
        os.makedirs(temp_dir, exist_ok=True)

        ext = 'mp3' if dtype == 'mp3' else 'mp4'
        output_path = os.path.join(temp_dir, f"video.{ext}")

        ydl_opts = {
            "quiet": True,
            "outtmpl": output_path,
            "format": "bestaudio/best" if dtype == "mp3" else "best",
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }] if dtype == "mp3" else []
        }

        # ✅ تأكد من وجود FFmpeg
        os.system("apt-get update && apt-get install -y ffmpeg")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(output_path):
            return jsonify({"error": "❌ File not found after download"}), 500

        # ✅ إرسال الملف مباشرة بدل إرجاع مسار
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
