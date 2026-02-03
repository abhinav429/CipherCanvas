# flask app - /api/hide and /api/reveal

import io
import uuid
from flask import Flask, request, jsonify, send_file, render_template

from crypto import encrypt, decrypt
from steganography import hide_in_image, extract_from_image, open_image
from compression import compress_image, decompress_image

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/hide", methods=["POST"])
def hide():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    if "message" not in request.form or "password" not in request.form:
        return jsonify({"error": "Message and password are required"}), 400

    file = request.files["image"]
    message = request.form["message"].strip()
    password = request.form["password"]

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400

    if file.filename == "" or not file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
        return jsonify({"error": "Please upload a valid image (PNG, JPG, BMP, GIF)"}), 400

    try:
        img = open_image(file.stream)
    except Exception as e:
        return jsonify({"error": f"Invalid image: {str(e)}"}), 400

    try:
        ciphertext = encrypt(message, password)
    except Exception as e:
        return jsonify({"error": f"Encryption failed: {str(e)}"}), 500

    try:
        stego = hide_in_image(img, ciphertext)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    png_bytes = compress_image(stego)
    filename = f"ciphercanvas_stego_{uuid.uuid4().hex[:8]}.png"
    return send_file(
        io.BytesIO(png_bytes),
        mimetype="image/png",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/api/reveal", methods=["POST"])
def reveal():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    if "password" not in request.form:
        return jsonify({"error": "Password is required"}), 400

    file = request.files["image"]
    password = request.form["password"]

    if file.filename == "":
        return jsonify({"error": "Please select an image file"}), 400

    try:
        img = decompress_image(file.read())
    except Exception as e:
        return jsonify({"error": f"Invalid or corrupted image: {str(e)}"}), 400

    try:
        data = extract_from_image(img)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        message = decrypt(data, password)
    except Exception as e:
        return jsonify({"error": "Decryption failed. Wrong password or not a CipherCanvas image."}), 400

    return jsonify({"message": message})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
