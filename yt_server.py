from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "✅ Server is running!"})

@app.route('/api/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'forcejson': True,
            'extract_flat': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get('formats', []):
            if f.get('url'):
                formats.append({
                    "quality": f.get('format_note'),
                    "ext": f.get('ext'),
                    "url": f.get('url')
                })

        return jsonify({
            "title": info.get('title'),
            "thumbnail": info.get('thumbnail'),
            "duration": info.get('duration'),
            "formats": formats
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
