from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "✅ YouTube Downloader Server is Running",
        "message": "Send a GET request to /api/download?url=YOUR_VIDEO_URL"
    })

@app.route('/api/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "❌ Missing video URL"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            formats = []
            for f in info.get('formats', []):
                if 'url' in f:
                    formats.append({
                        'itag': f.get('format_id'),
                        'ext': f.get('ext'),
                        'quality': f.get('format_note'),
                        'filesize': f.get('filesize', 0),
                        'url': f.get('url')
                    })

            return jsonify({
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "formats": formats
            })

    except Exception as e:
        return jsonify({"error": f"⚠️ Server Error: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
