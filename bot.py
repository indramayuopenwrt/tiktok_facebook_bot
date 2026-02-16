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
    if '/reel' in url:
        url = url.replace('/reel', '/watch')
    elif '/share/' in url:
        if not 'v=' in url:
            url += '?v=' + url.split('/')[-1]
    return url

# Fungsi untuk mendownload video dari TikTok atau Facebook dengan progress bar
def download_video(url, platform, update):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'extract_flat': False,
        'progress_hooks': [lambda d: progress_bar(d, update)]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if platform == "tiktok":
            info = ydl.extract_info(url, download=True)
        elif platform == "facebook":
            url = convert_facebook_url(url)
            info = ydl.extract_info(url, download=True)
        else:
            raise ValueError("Unsupported platform")

        description = info.get('description', 'No description available.')
        title = info.get('title', 'No title available.')
        video_url = info['url']
        file_path = ydl.prepare_filename(info)

        return file_path, video_url, title, description

def progress_bar(d, update):
    if d['status'] == 'downloading':
        total_size = d.get('total_bytes', 0)
        downloaded = d.get('downloaded_bytes', 0)
        if total_size > 0:
            percent = (downloaded / total_size) * 100
        else:
            percent = 0
        speed = d.get('speed', 0) / 1024
        eta = d.get('eta', 0)
        update.message.edit_text(f"Downloading... {percent:.2f}% ({downloaded / 1024:.2f}KB/{total_size / 1024:.2f}KB) at {speed:.2f}KB/s. ETA: {eta}s")

# Fungsi untuk menangani command /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hi! Send me a TikTok or Facebook video link, and I will download it for you!")

# Fungsi untuk menangani pengunduhan video
async def download(update: Update, context: CallbackContext):
    url = update.message.text
    await update.message.reply_text("Processing, please wait...")

    platform = detect_platform(url)

    if not platform:
        await update.message.reply_text("Sorry, I can't process this URL. Please provide a TikTok or Facebook link.")
        return
    await update.message.reply_text(f"Detected platform: {platform}")

    try:
        file_path, video_url, title, description = download_video(url, platform, update)
        await update.message.reply_text(f"Title: {title}\nDescription: {description}")
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="Here is your video.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

# Fungsi utama untuk menjalankan bot
def main():
    token = "8305181648:AAFqVhMdh2vBiLzb9N3z3H5AXt7LKZMEZDk"
    application = Application.builder().token(token).build()

    # Menjalankan webhook
    application.run_webhook(
        listen="0.0.0.0",  # Bot bisa diakses dari luar
        port=5000,  # Port yang digunakan oleh Railway
        url_path="8305181648:AAFqVhMdh2vBiLzb9N3z3H5AXt7LKZMEZDk",  # Ganti dengan token bot Telegrammu
        webhook_url=f"tiktok_facebook_bottiktokfacebookbot-production.up.railway.appOnline/8305181648:AAFqVhMdh2vBiLzb9N3z3H5AXt7LKZMEZDk"  # URL aplikasi Railway
    )

if __name__ == '__main__':
    main()
