import os
import logging
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import yt_dlp
from moviepy.editor import VideoFileClip

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

# Fungsi untuk menghapus watermark menggunakan moviepy
def remove_watermark(input_path, output_path):
    clip = VideoFileClip(input_path)
    cropped_clip = clip.crop(y1=50)  # Adjust this value based on your video
    cropped_clip.write_videofile(output_path)

# Fungsi untuk mendownload video dari TikTok atau Facebook
def download_video(url, platform):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
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
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! Send me a TikTok or Facebook video link, and I will download it for you!")

# Fungsi untuk menangani pengunduhan video
def download(update: Update, context: CallbackContext):
    url = update.message.text
    update.message.reply_text("Processing, please wait...")

    # Deteksi platform dari URL
    platform = detect_platform(url)

    if not platform:
        update.message.reply_text("Sorry, I can't process this URL. Please provide a TikTok or Facebook link.")
        return

    try:
        file_path, video_url = download_video(url, platform)
        update.message.reply_text(f"Video downloaded successfully! Video URL: {video_url}")

        # Hapus watermark jika diperlukan
        output_path = f"downloads/cleaned_{os.path.basename(file_path)}"
        remove_watermark(file_path, output_path)

        update.message.reply_video(video=open(output_path, 'rb'), caption="Here is your video without watermark.")

    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")

# Fungsi utama untuk menjalankan bot
def main():
    token = "8305181648:AAFqVhMdh2vBiLzb9N3z3H5AXt7LKZMEZDk"  # Ganti dengan token bot Telegrammu
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
