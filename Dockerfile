# Gunakan image Python terbaru
FROM python:3.9-slim

# Install beberapa dependensi dasar untuk membangun dan menginstal ffmpeg
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    libx264-dev \
    libavcodec-dev \
    libavformat-dev

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode bot ke dalam container
COPY . .

# Menjalankan aplikasi
CMD ["python", "bot.py"]
