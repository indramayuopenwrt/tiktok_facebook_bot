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

# Fungsi untuk mendownload video dari TikTok atau Facebook
def download_video(url, platform):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Mendapatkan video dan audio terbaik
        'noplaylist': True,
        'quiet': True,
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Tentukan path file output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if platform == "tiktok":
            info = ydl.extract_info(url, download=True)
        elif platform == "facebook":
            info = ydl.extract_info(url, download=True)
        else:
            raise ValueError("Unsupported platform")

        video_url = info['url']
        file_path = ydl.prepare_filename(info)
        return file_path, video_url

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
        file_path, video_url = download_video(url, platform)
        await update.message.reply_text(f"Video downloaded successfully! Video URL: {video_url}")

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
