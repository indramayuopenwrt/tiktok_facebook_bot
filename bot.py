from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
import yt_dlp
import subprocess
from tqdm import tqdm

# Fungsi untuk mengunduh video TikTok dengan kualitas terbaik menggunakan yt-dlp
def get_tiktok_video(url):
    ydl_opts = {
        'quiet': True,
        'extract_audio': False,
        'format': 'bestvideo+bestaudio/best',  # Memilih kualitas video terbaik
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Lokasi penyimpanan video
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return info_dict['url']  # Mengembalikan URL video yang sudah diunduh

# Fungsi untuk mengunduh video Facebook dengan kualitas terbaik menggunakan yt-dlp
def get_facebook_video(url):
    ydl_opts = {
        'quiet': True,
        'extract_audio': False,
        'format': 'bestvideo+bestaudio/best',  # Memilih kualitas video terbaik
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Lokasi penyimpanan video
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return info_dict['url']  # Mengembalikan URL video yang sudah diunduh

# Fungsi untuk menghapus watermark dari video (menggunakan ffmpeg)
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
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Welcome! Send me a TikTok or Facebook video link.')

# Fungsi untuk menangani pengunduhan video dari TikTok atau Facebook
async def download(update: Update, context: CallbackContext):
    url = update.message.text
    if "tiktok.com" in url:
        await update.message.reply_text("Downloading TikTok video...")
        video_url = get_tiktok_video(url)  # Mendapatkan URL video TikTok
    elif "facebook.com" in url:
        await update.message.reply_text("Downloading Facebook video...")
        video_url = get_facebook_video(url)  # Mendapatkan URL video Facebook
    else:
        await update.message.reply_text('Link not recognized. Please send a valid TikTok or Facebook link.')
        return

    await update.message.reply_text("Sending video...")
    await update.message.reply_video(video_url)  # Mengirimkan video ke pengguna

# Fungsi utama untuk menjalankan bot
def main():
    application = Application.builder().token('8305181648:AAFqVhMdh2vBiLzb9N3z3H5AXt7LKZMEZDk').build()  # Ganti dengan token API Anda

    # Menambahkan handler
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('download', download))

    # Memulai bot dengan polling
    application.run_polling(drop_pending_updates=True)  # Pastikan tidak ada update yang tertunda

if __name__ == '__main__':
    main()  # Menjalankan aplikasi secara langsung
