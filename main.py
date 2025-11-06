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
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Falta parámetro 'url'"}), 400

    try:
        # Llamada a la API gratuita de SnapSave.io
        api_url = "https://api.snapsave.app/api/ajaxSearch"
        payload = {"q": url, "vt": "home"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(api_url, data=payload, headers=headers, timeout=15)

        if response.status_code != 200:
            return jsonify({"error": "No se pudo conectar a SnapSave"}), 500

        data = response.json()

        # Validar respuesta
        if "data" not in data or not data["data"]:
            return jsonify({"error": "No se encontraron enlaces"}), 404

        # Extraer enlace HD (720p o superior si existe)
        links = data["data"]
        hd_link = None
        for item in links:
            quality = item.get("quality", "")
            if "720" in quality or "1080" in quality:
                hd_link = item.get("url")
                break

        # Si no hay HD, toma el primero disponible
        if not hd_link:
            hd_link = links[0].get("url")

        return jsonify({
            "title": data.get("title", "video"),
            "download_url": hd_link,
            "formats": links
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)




