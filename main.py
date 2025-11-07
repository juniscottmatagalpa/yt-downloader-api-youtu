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

        # Llamar al servicio de SnapSave (sin proxy, conexión directa)
        response = requests.post(api_url, data=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        if not data.get("data"):
            return jsonify({"error": "No se encontraron formatos válidos."}), 404

        # Seleccionar mejor formato (HD si existe)
        formats = data["data"]
        hd = next((v for v in formats if "720" in v["quality"] or "1080" in v["quality"]), formats[0])

        return jsonify({
            "title": data.get("title", "Video sin título"),
            "download_url": hd["url"],
            "formats": formats
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


