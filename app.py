from flask import Flask, jsonify, render_template, send_file, request
from braille_conversion import convert_to_braille, speak
from PIL import Image
import pytesseract
import os
from werkzeug.utils import secure_filename
from threading import Thread
import time

# Configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
AUDIO_PATH = 'static/audio/temp.mp3'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.dirname(AUDIO_PATH), exist_ok=True)

# Utility: Check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Utility: Delayed cleanup
def delayed_cleanup(path, delay=60):
    time.sleep(delay)
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"[INFO] Deleted: {path}")
        except Exception as e:
            print(f"[ERROR] Failed to delete {path}: {e}")

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_file('favicon.ico', mimetype='image/x-icon')

# Cover image route
@app.route('/coverimage')
def cover_image():
    return send_file('samples/cover.jpg', mimetype='image/jpeg')

# ✅ Serve MP3 audio safely
@app.route('/audio')
def stream_audio():
    try:
        if os.path.exists(AUDIO_PATH):
            return send_file(AUDIO_PATH, mimetype='audio/mpeg', as_attachment=False)
        else:
            return jsonify({'error': 'Audio not generated yet'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to stream audio: {str(e)}'}), 500

# 🖼️ Image upload route
@app.route('/process_image', methods=['POST'])
def process_image():
    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        return jsonify({'error': 'No image file provided'}), 400
    if not allowed_file(image_file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = secure_filename(image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)

    try:
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        braille_text = convert_to_braille(extracted_text)

        # Start TTS and cleanup in background
        Thread(target=speak, args=(extracted_text,)).start()
        Thread(target=delayed_cleanup, args=(AUDIO_PATH, 30)).start()
        Thread(target=delayed_cleanup, args=(image_path, 30)).start()

        # Wait for audio creation (max 3s)
        for _ in range(30):
            if os.path.exists(AUDIO_PATH):
                break
            time.sleep(0.1)

        return jsonify({
            'extracted_text': extracted_text.strip(),
            'braille_text': braille_text.strip()
        })

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

# 🔤 Manual text route
@app.route('/convert_text', methods=['POST'])
def convert_text():
    user_text = request.form.get('user_text', '').strip()
    if not user_text:
        return jsonify({'error': 'No text input provided'}), 400

    try:
        braille_text = convert_to_braille(user_text)

        # Start TTS and cleanup
        Thread(target=speak, args=(user_text,)).start()
        Thread(target=delayed_cleanup, args=(AUDIO_PATH, 30)).start()

        # Wait for audio creation (max 3s)
        for _ in range(30):
            if os.path.exists(AUDIO_PATH):
                break
            time.sleep(0.1)

        return jsonify({
            'original_text': user_text,
            'braille_text': braille_text
        })

    except Exception as e:
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
