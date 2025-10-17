# 📁 yt_server.py
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
        # ✅ قراءة خيار الدمج من الرابط (merge=1 يعني دمج الصوت مع الفيديو)
        merge = request.args.get('merge')

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "forcejson": True,
            "extract_flat": False,
            "noplaylist": True,
        }

        # ✅ تحديد نوع التحميل المطلوب
        if merge:
            # 🎬 فيديو + صوت (مُدمج)
            ydl_opts["format"] = "bestvideo+bestaudio/best"
        else:
            # 🎥 فيديو فقط (بدون صوت)
            ydl_opts["format"] = "bestvideo/best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if not f.get("url"):
                continue

            acodec = f.get("acodec") or ""
            vcodec = f.get("vcodec") or ""
            ext = f.get("ext") or "mp4"

            # 🔹 تحديد إذا كان صوت فقط أو فيديو فقط
            is_audio = (vcodec == "none" or vcodec == "") and acodec != "none"
            is_video = vcodec != "none" and vcodec != ""

            # 🔹 بناء التفاصيل
            if is_audio or is_video:
                quality = (
                    f.get("format_note")
                    or f.get("resolution")
                    or f.get("abr")
                    or "unknown"
                )
                formats.append({
                    "format_id": f.get("format_id"),
                    "format_note": quality,
                    "ext": "mp3" if is_audio else "mp4",
                    "acodec": acodec,
                    "vcodec": vcodec,
                    "filesize": f.get("filesize") or 0,
                    "url": f.get("url"),
                    "type": "audio" if is_audio else "video"
                })

        # 🔹 ترتيب حسب الجودة تقريبًا (أعلى جودة أولًا)
        videos = [f for f in formats if f["type"] == "video"]
        audios = [f for f in formats if f["type"] == "audio"]

        videos = sorted(videos, key=lambda x: str(x["format_note"]))
        audios = sorted(audios, key=lambda x: str(x["format_note"]))

        # 🔹 اقتصار على 5 فقط من كل نوع
        videos = videos[:5]
        audios = audios[:5]
        formats = videos + audios

        print(f"🎬 Found {len(videos)} videos and 🎵 {len(audios)} audios")
        print(f"🧩 Merge mode: {'ON (video+audio)' if merge else 'OFF (video only)'}")

        if not formats:
            return jsonify({"error": "No formats found"}), 404

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "formats": formats
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # ✅ السيرفر المحلي
    app.run(host='0.0.0.0', port=10000)
