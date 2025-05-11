# Image Text Assistive Reader Web App

A web-based assistive technology tool that:
- Extracts text from images using OCR
- Converts text to Braille representation
- Reads text aloud using Text-to-Speech (TTS)
- Built with Python, Flask, Tesseract OCR, gTTS, and Docker.

## 📦 Features
- 🖼️ Image Upload for OCR
- 🔤 Manual Text Input
- ⠿ Braille Text Output
- 🔊 Real-time Audio Feedback (TTS)
- 🐳 Docker Support

## 🚀 How to Run (Locally)

```bash
# 1. Clone the repo
git clone https://github.com/your-username/braille-reader-app.git
cd braille-reader-app

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
🐳 How to Build & Run with Docker
bash
Copy
Edit
# Build the Docker image
docker build -t braille-reader .

# Run the container
docker run -p 5000:5000 braille-reader
🧠 Tech Stack
Python

Flask

OpenCV

pytesseract

gTTS

Docker

📁 Directory Structure
arduino
Copy
Edit
/app
 ├── app.py
 ├── braille_conversion.py
 ├── static/
 │   └── audio/
 ├── templates/
 │   └── index.html
 ├── uploads/
 ├── requirements.txt
 └── Dockerfile
🙌 Credits
Made with ❤️ for visually impaired support using AI and accessible tech.

yaml
Copy
Edit

---

✅ 4. `.gitignore`
```gitignore
__pycache__/
*.pyc
venv/
.env
uploads/
static/audio/


✅ 5. Folder Structure Example
Make sure you include:

templates/index.html

static/audio/ (empty or in .gitignore)

uploads/ folder (empty or in .gitignore)

app.py, braille_conversion.py

