import os
import cv2
from TikTokApi import TikTokApi
from facebook_scraper import get_posts
import youtube_dl
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from tqdm import tqdm

# Fungsi untuk mengunduh video TikTok dengan kualitas terbaik (HD)
def download_tiktok_video(url, user_id):
    api = TikTokApi.get_instance()
    video = api.video(url=url)

    # Menyaring kualitas terbaik video yang tersedia
    video_data = video.bytes()
    filename = f"tiktok_video_{user_id}.mp4"

    with open(filename, 'wb') as f:
        f.write(video_data)

    return filename

# Fungsi untuk mengunduh video Facebook dengan kualitas terbaik (HD)
def download_facebook_video(url, user_id):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Memilih kualitas terbaik (HD)
        'outtmpl': f'facebook_video_{user_id}.mp4'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return f"facebook_video_{user_id}.mp4"

# Fungsi untuk mendeteksi dan mengunduh video berdasarkan URL
def detect_and_download_video(url, user_id):
    if "tiktok.com" in url:
        return download_tiktok_video(url, user_id)
    elif "facebook.com" in url:
        return download_facebook_video(url, user_id)
    else:
        return None

# Fungsi untuk menghapus watermark
def remove_watermark(input_video_path, user_id):
    output_video_path = f"no_watermark_{user_id}.mp4"
    cap = cv2.VideoCapture(input_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = frame[0:height-50, 50:width-50]  # Crop the watermark area
        out.write(frame)

    cap.release()
    out.release()
    return output_video_path

# Fungsi untuk mengambil metadata video TikTok
def get_tiktok_metadata(url):
    api = TikTokApi.get_instance()
    video = api.video(url=url)
    metadata = {
        'description': video.description,
        'author': video.author.username,
        'likes': video.stats.digg_count,
        'comments': video.stats.comment_count,
        'shares': video.stats.share_count
    }
    return metadata

# Fungsi untuk mengambil metadata video Facebook
def get_facebook_metadata(url):
    posts = get_posts(url, pages=1)
    for post in posts:
        metadata = {
            'description': post['text'],
            'likes': post['likes'],
            'comments': post['comments'],
            'shares': post['shares']
        }
        return metadata

# Command /start untuk bot Telegram
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Halo! Kirimkan saya link video TikTok atau Facebook, dan saya akan mengunduhnya untuk Anda.")

# Handler untuk mengunduh video berdasarkan URL
def download(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    url = update.message.text
    update.message.reply_text("Mengunduh video... harap tunggu.")

    # Mengunduh video dan mengirimkan video ke pengguna
    filename = detect_and_download_video(url, user_id)

    if filename:
        update.message.reply_text(f"Video berhasil diunduh. Mengirimkan video...")
        with open(filename, 'rb') as video_file:
            update.message.reply_video(video_file)
        os.remove(filename)  # Menghapus file video setelah dikirim
    else:
        update.message.reply_text("URL tidak valid atau tidak didukung. Coba kirim link TikTok atau Facebook.")

# Fungsi utama untuk menjalankan bot Telegram
def main():
    # Ganti dengan token bot Telegram Anda yang didapat dari BotFather
    token = "YOUR_BOT_API_TOKEN"

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # Menambahkan handler untuk /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Menambahkan handler untuk pesan teks (URL)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download))

    # Memulai bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
