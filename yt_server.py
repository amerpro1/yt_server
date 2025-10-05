from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "✅ Universal Video Downloader Server is Running"})

@app.route('/info')
def info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing video URL"}), 400

    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "uploader": info.get("uploader"),
                "duration": info.get("duration"),
                "ext": info.get("ext")
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download')
def download():
    url = request.args.get("url")
    media_type = request.args.get("type", "mp4")

    if not url:
        return jsonify({"error": "Missing video URL"}), 400

    try:
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, f"%(title)s.{'mp3' if media_type == 'mp3' else 'mp4'}")

        ydl_opts = {
            "outtmpl": output_path,
            "quiet": True,
            "format": "bestaudio/best" if media_type == "mp3" else "bestvideo+bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }] if media_type == "mp3" else []
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        return send_file(file_path, as_attachment=True)
    except Exception as e:
