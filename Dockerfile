FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first for caching layers
COPY requirements.txt .

# Install system dependencies including Tesseract OCR, mpg123, and espeak
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    mpg123                # For playing MP3s (used by playsound)


# Install Python dependencies
RUN pip install "numpy<2"    
RUN pip install pyttsx3
RUN pip install playsound
RUN pip install gTTS

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into the container
COPY . .

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
