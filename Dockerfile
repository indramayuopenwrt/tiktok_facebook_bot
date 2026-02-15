# Gunakan image Python terbaru
FROM python:3.9-slim

# Update package list dan install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode bot ke dalam container
COPY . .

# Menjalankan aplikasi
CMD ["python", "bot.py"]
