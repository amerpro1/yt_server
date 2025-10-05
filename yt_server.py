# yt_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)  # للسماح لتطبيقك Flutter بالاتصال عبر المتصفح/HTTP

YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    # مهم جداً لبعض المواقع (مثلاً إنستغرام/تيك توك) لتخطي الحظر المؤقت
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0 Safari/537.36"
    }
}

def extract_info(url: str):
    with YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
        # بعض الروابط (Shorts/Reels) ترجّع playlist-like؛ نأخذ المدخل الأول
        if "_type" in info and info["_type"] == "url":
            info = ydl.extract_info(info["url"], download=False)
        return info

@app.route("/")
def root():
    return jsonify({"ok": True, "service": "yt_server", "status": "running"})

@app.route("/info", methods=["GET", "POST"])
def info():
    """
    يَستقبل:
      GET  /info?url=...
      أو POST JSON: { "url": "..." }

    يُعيد:
      {
        "title": "...",
        "uploader": "...",
        "duration": 123,              # ثواني
        "thumbnail": "https://...",
        "formats": [
          {
            "type": "video",          # video | audio
            "ext": "mp4",
            "height": 720,
            "fps": 30,
            "abr": null,              # للـ audio فقط (Kbps)
            "filesize": 12345678,     # قد يكون null لو غير معروف
            "url": "https://direct.cdn/.."
          },
          ...
        ]
      }
    """
    try:
      data = request.get_json(silent=True) or {}
      url = request.args.get("url") or data.get("url")
      if not url:
          return jsonify({"error": "missing url"}), 400

      info = extract_info(url)

      title = info.get("title")
      thumbnail = info.get("thumbnail") or (info.get("thumbnails") or [{}])[-1].get("url")
      uploader = info.get("uploader") or info.get("channel") or info.get("uploader_id")
      duration = info.get("duration")

      fmts = []
      for f in info.get("formats", []):
          # استبعاد فورمات بدون رابط
          direct_url = f.get("url")
          if not direct_url:
              continue

          vcodec = f.get("vcodec")
          acodec = f.get("acodec")
          ext = (f.get("ext") or "").lower()

          # نوع Video (يحوي صوت وصورة)
          if vcodec not in (None, "none") and acodec not in (None, "none"):
              fmts.append({
                  "type": "video",
                  "ext": ext,
                  "height": f.get("height"),
                  "fps": f.get("fps"),
                  "filesize": f.get("filesize") or f.get("filesize_approx"),
                  "url": direct_url,
              })
          # نوع Audio فقط
          elif vcodec in (None, "none") and acodec not in (None, "none"):
              abr = f.get("abr")  # Kbps
              if isinstance(abr, float):
                  abr = int(round(abr))
              fmts.append({
                  "type": "audio",
                  "ext": ext,         # غالباً m4a أو webm
                  "abr": abr,
                  "filesize": f.get("filesize") or f.get("filesize_approx"),
                  "url": direct_url,
              })
          else:
              # تجاهل الباقي (فيديو بدون صوت أو ملفات بيانات)
              continue

      # ترتيب: الفيديوهات أولاً من الأعلى جودة، ثم الصوتيات حسب الـ abr
      videos = sorted([x for x in fmts if x["type"] == "video"],
                      key=lambda x: (x.get("height") or 0, x.get("fps") or 0),
                      reverse=True)
      audios = sorted([x for x in fmts if x["type"] == "audio"],
                      key=lambda x: (x.get("abr") or 0),
                      reverse=True)

      return jsonify({
          "title": title,
          "uploader": uploader,
          "duration": duration,
          "thumbnail": thumbnail,
          "formats": videos + audios
      })

    except Exception as e:
      # أي خطأ (مثلاً رابط غير صحيح) يرجّع 400 مع رسالة واضحة
      return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    # للتشغيل محلياً فقط: python yt_server.py
    app.run(host="0.0.0.0", port=8000)
