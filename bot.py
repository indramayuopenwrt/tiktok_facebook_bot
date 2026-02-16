import os
import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import yt_dlp

# Mengatur logging untuk debug
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Fungsi untuk mendeteksi platform dari URL
def detect_platform(url):
    tiktok_pattern = r'(https?://(?:www\.)?tiktok\.com/.*)'
    facebook_pattern = r'(https?://(?:www\.)?facebook\.com/.*)'

    if re.match(tiktok_pattern, url):
        return "tiktok"
    elif re.match(facebook_pattern, url):
        return "facebook"
    else:
        return None

# Fungsi untuk memastikan link Facebook adalah publik
def convert_facebook_url(url):
    # Mencari URL yang memiliki '/reel' dan mengubahnya menjadi link 'watch' publik
    if '/reel' in url:
        url = url.replace('/reel', '/watch')
    elif '/share/' in url:  # Menangani URL Facebook berbagi
        if not 'v=' in url:
            url += '?v=' + url.split('/')[-1]  # Menambahkan query parameter untuk video
    return url

# Fungsi untuk mendownload video dari TikTok atau Facebook dengan progress bar
def download_video(url, platform, update):
    ydl_opts = {
        'format': 'best',  # Pilih format terbaik yang sudah dipadukan video + audio
        'noplaylist': True,
        'quiet': True,
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',  # Gabungkan video dan audio dalam satu format mp4
        'extract_flat': False,  # Untuk memastikan kita mendapatkan metadata
        'progress_hooks': [lambda d: progress_bar(d, update)]  # Update progress bar real-time
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if platform == "tiktok":
            info = ydl.extract_info(url, download=True)
        elif platform == "facebook":
            # Mengonversi URL Facebook jika perlu
            url = convert_facebook_url(url)
            info = ydl.extract_info(url, download=True)
        else:
            raise ValueError("Unsupported platform")

        # Ambil metadata (judul, deskripsi, dll)
        description = info.get('description', 'No description available.')
        title = info.get('title', 'No title available.')
        video_url = info['url']
        file_path = ydl.prepare_filename(info)
        
        return file_path, video_url, title, description

# Fungsi untuk menangani update progress bar
def progress_bar(d, update):
    if d['status'] == 'downloading':
        # Proses pengunduhan
        total_size = d.get('total_bytes', 0)
        downloaded = d.get('downloaded_bytes', 0)
        
        # Menghindari pembagian dengan None atau 0
        if total_size > 0:
            percent = (downloaded / total_size) * 100
        else:
            percent = 0
        
        speed = d.get('speed', 0) / 1024  # Kecepatan dalam KB/s
        eta = d.get('eta', 0)

        # Kirimkan progress ke Telegram
        update.message.edit_text(f"Downloading... {percent:.2f}% ({downloaded / 1024:.2f}KB/{total_size / 1024:.2f}KB) at {speed:.2f}KB/s. ETA: {eta}s")

# Fungsi untuk menangani command /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hi! Send me a TikTok or Facebook video link, and I will download it for you!")

# Fungsi untuk menangani pengunduhan video
async def download(update: Update, context: CallbackContext):
    url = update.message.text
    await update.message.reply_text("Processing, please wait...")

    # Deteksi platform dari URL
    platform = detect_platform(url)

    if not platform:
        await update.message.reply_text("Sorry, I can't process this URL. Please provide a TikTok or Facebook link.")
        return
    await update.message.reply_text(f"Detected platform: {platform}")

    try:
        # Mulai mengunduh video dengan progress bar
        file_path, video_url, title, description = download_video(url, platform, update)
        
        # Kirim metadata deskripsi bersama dengan video
        await update.message.reply_text(f"Title: {title}\nDescription: {description}")

        # Kirim video yang sudah diunduh
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="Here is your video.")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

# Fungsi utama untuk menjalankan bot
def main():
    token = "8305181648:AAFqVhMdh2vBiLzb9N3z3H5AXt7LKZMEZDk"  # Ganti dengan token bot Telegrammu
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    application.run_polling()

if __name__ == '__main__':
    main()
