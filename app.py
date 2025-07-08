import os
import tempfile
from flask import Flask, request, jsonify, send_file
import subprocess

app = Flask(__name__)
API_KEY = os.environ.get("API_KEY")

@app.route("/ocr", methods=["POST"])
def ocr_pdf():
    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as input_pdf:
        file.save(input_pdf.name)
        output_path = input_pdf.name.replace(".pdf", "_ocr.pdf")

        try:
            subprocess.run(["ocrmypdf", input_pdf.name, output_path], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "OCR failed", "details": str(e)}), 500

        return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
