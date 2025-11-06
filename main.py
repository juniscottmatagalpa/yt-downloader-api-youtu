from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import yt_dlp
import tempfile
import os
import shutil

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "✅ Servidor de descargas activo (Render)"

@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        url = data.get("url")
        quality = data.get("quality", "high")

        if not url:
            return jsonify({"error": "Falta parámetro 'url'"}), 400

        temp_dir = tempfile.mkdtemp()
        ext = "mp4"

        if quality == "audio":
            fmt = "bestaudio/best"
            ext = "mp3"
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        elif quality == "low":
            fmt = "best[height<=480][ext=mp4]/best"
            postprocessors = []
        else:
            fmt = "best[ext=mp4]/best"
            postprocessors = []

        ydl_opts = {
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "format": fmt,
            "quiet": True,
            "noplaylist": True,
            "postprocessors": postprocessors
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if quality == "audio":
                filename = os.path.splitext(filename)[0] + ".mp3"

        if not os.path.exists(filename):
            return jsonify({"error": "No se pudo descargar el archivo"}), 500

        @after_this_request
        def cleanup(response):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return response

        return send_file(filename, as_attachment=True, download_name=os.path.basename(filename))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


