from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from TikTokApi import TikTokApi
import yt_dlp
import subprocess
from tqdm import tqdm

# Fungsi untuk mengunduh video TikTok dengan kualitas terbaik
def get_tiktok_video(url):
    with TikTokApi() as api:
        video = api.video(url)
        # Mendapatkan video dengan kualitas terbaik
        best_quality_video = video.bytes()
        return best_quality_video

# Fungsi untuk mengunduh video Facebook dengan kualitas terbaik
def get_facebook_video(url):
    ydl_opts = {
        'quiet': True,
        'extract_audio': False,
        'format': 'bestvideo+bestaudio/best',  # Memilih kualitas video dan audio terbaik
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return info_dict['url']  # Mengembalikan URL video dengan kualitas terbaik

# Fungsi untuk menghapus watermark
def remove_watermark(input_video):
    output_video = 'output.mp4'
    cmd = f'ffmpeg -i {input_video} -vf "delogo=x=10:y=10:w=200:h=100" -c:a copy {output_video}'
    subprocess.run(cmd, shell=True)
    return output_video

# Fungsi untuk mengunduh video dan menampilkan progress bar
def download_video(url):
    with requests.get(url, stream=True) as r:
        total_size = int(r.headers.get('content-length', 0))
        with open("video.mp4", "wb") as f, tqdm(
            desc="Downloading video", total=total_size, unit="B", unit_scale=True
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

# Fungsi untuk memulai interaksi dengan bot Telegram
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome! Send me a TikTok or Facebook video link.')

# Fungsi untuk menangani pengunduhan video
def download(update: Update, context: CallbackContext):
    url = update.message.text
    if "tiktok.com" in url:
        video = get_tiktok_video(url)
        video_path = save_video(video)  # Simpan video ke file
    elif "facebook.com" in url:
        video_url = get_facebook_video(url)
        video_path = video_url  # Mendapatkan URL video dengan kualitas terbaik
    else:
        update.message.reply_text('Link not recognized. Please send a valid TikTok or Facebook link.')
        return

    update.message.reply_text("Downloading video...")
    video_with_watermark_removed = remove_watermark(video_path)  # Hapus watermark
    update.message.reply_text("Sending video...")
    update.message.reply_video(video_with_watermark_removed)  # Kirim video ke user

# Fungsi utama untuk menjalankan bot
def main():
    updater = Updater('8305181648:AAFqVhMdh2vBiLzb9N3z3H5AXt7LKZMEZDk')  # Ganti dengan token API Anda
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('download', download))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()