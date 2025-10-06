from flask import Flask, request, jsonify
import yt_dlp
import os
import tempfile

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "✅ Server is running!", "version": "3.0"})

@app.route("/info")
def info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "❌ URL is required"}), 400

    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info_dict.get("title"),
                "thumbnail": info_dict.get("thumbnail"),
                "duration": info_dict.get("duration"),
                "extractor": info_dict.get("extractor"),
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download")
def download():
    url = request.args.get("url")
    media_type = request.args.get("type", "mp4")

    if not url:
        return jsonify({"error": "❌ URL is required"}), 400

    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"download.{'mp3' if media_type == 'mp3' else 'mp4'}")

        ydl_opts = {
            "format": "bestaudio/best" if media_type == "mp3" else "best",
            "outtmpl": output_path,
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }] if media_type == "mp3" else [],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({
            "status": "✅ Success",
            "file_url": output_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
