import re
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import yt_dlp

# Fungsi untuk mendeteksi platform (TikTok atau Facebook) dari URL
def detect_platform(url):
    tiktok_pattern = r"tiktok\\.com"
    facebook_pattern = r"facebook\\.com"

    if re.search(tiktok_pattern, url):
        return "tiktok"
    elif re.search(facebook_pattern, url):
        return "facebook"
    else:
        return None

# Fungsi untuk mendapatkan metadata dari video
def get_metadata(url):
    ydl_opts = {
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get('title', 'No title available')
        description = info_dict.get('description', 'No description available')
        duration = info_dict.get('duration', 'No duration available')
        uploader = info_dict.get('uploader', 'No uploader information')
        thumbnail = info_dict.get('thumbnail', 'No thumbnail available')

        metadata = f"""
        Title: {title}
        Description: {description}
        Duration: {duration} seconds
        Uploader: {uploader}
        Thumbnail: {thumbnail}
        """
        return metadata

# Fungsi untuk mengunduh video TikTok tanpa watermark
def download_tiktok(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'progress_hooks': [progress_hook]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        return result['id'] + '.' + result['ext']

# Fungsi untuk mengunduh video Facebook tanpa watermark
def download_facebook(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'progress_hooks': [progress_hook]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        return result['id'] + '.' + result['ext']

# Progress bar callback
def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['filename']} {d['_percent_str']}")

# Fungsi untuk mengunduh video berdasarkan link yang dikirimkan tanpa perintah
def handle_message(update: Update, context: CallbackContext):
    url = update.message.text

    # Deteksi platform berdasarkan URL
    platform = detect_platform(url)
    if not platform:
        update.message.reply_text("Invalid link! Please provide a valid TikTok or Facebook link.")
        return

    # Mendapatkan metadata dan mengirimkannya
    metadata = get_metadata(url)
    update.message.reply_text(f"Metadata:\n{metadata}")

    if platform == "tiktok":
        update.message.reply_text("Downloading TikTok video...")
        filename = download_tiktok(url)
    elif platform == "facebook":
        update.message.reply_text("Downloading Facebook video...")
        filename = download_facebook(url)

    # Kirimkan video setelah diunduh
    with open(f'downloads/{filename}', 'rb') as video:
        update.message.reply_video(video)

# Fungsi untuk scraper TikTok by username (command /ttmass)
def ttmass(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Please provide a TikTok username. Example: /ttmass username")
        return

    username = context.args[0]
    url_tiktok = f"https://www.tiktok.com/@{username}"

    update.message.reply_text(f"Scraping TikTok videos from @{username}...")

    # Mendapatkan metadata dan mengirimkannya
    metadata = get_metadata(url_tiktok)
    update.message.reply_text(f"Metadata:\n{metadata}")

    try:
        filename = download_tiktok(url_tiktok)
        with open(f'downloads/{filename}', 'rb') as video:
            update.message.reply_video(video)
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}. Could not scrape videos from this username.")

# Fungsi utama untuk menjalankan bot
def main():
    TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Gantilah dengan token bot Telegram kamu

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Menambahkan handler untuk command /ttmass
    dp.add_handler(CommandHandler("ttmass", ttmass))

    # Menambahkan handler untuk menangani pesan yang berisi link
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()