from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "✅ Servidor activo - Descargador YouTube HD (SnapSave API Gratis)"

@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "Falta parámetro 'url'"}), 400

        api_url = "https://api.snapsave.app/api/ajaxSearch"
        payload = {"q": url, "vt": "home"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }

        response = requests.post(api_url, data=payload, headers=headers, timeout=20)
        response.raise_for_status()
        result = response.json()

        if not result.get("data"):
            return jsonify({"error": "No se encontraron formatos válidos."}), 404

        formats = result["data"]
        hd = next((v for v in formats if "720" in v["quality"] or "1080" in v["quality"]), formats[0])

        return jsonify({
            "title": result.get("title", "Video sin título"),
            "download_url": hd["url"],
            "formats": formats
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)



