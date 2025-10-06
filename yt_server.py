from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

RAPIDAPI_KEY = "177531b8e2mshca7e034984ce5bbp1a0046jsnff3ed7629b4d"
RAPIDAPI_HOST = "all-video-downloader1.p.rapidapi.com"

@app.route('/')
def home():
    return jsonify({"status": "✅ RapidAPI server online", "version": "3.0"})

@app.route('/info')
def info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        response = requests.get(
            f"https://{RAPIDAPI_HOST}/getVideoDetails",
            headers={
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": RAPIDAPI_HOST
            },
            params={"video_url": url},
            timeout=20
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download')
def download():
    url = request.args.get('url')
    media_type = request.args.get('type', 'mp4')

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        response = requests.get(
            f"https://{RAPIDAPI_HOST}/getSocialVideo",
            headers={
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": RAPIDAPI_HOST
            },
            params={
                "url": url,
                "video_format": "mp4" if media_type == "mp4" else "mp3"
            },
            timeout=30
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
