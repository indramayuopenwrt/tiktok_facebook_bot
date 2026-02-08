
import os
import zipfile
import shutil
import yt_dlp
from datetime import datetime
from dateutil.parser import parse as dateparse
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
BASE_DIR = "downloads"
os.makedirs(BASE_DIR, exist_ok=True)

def progress_bar(percent):
    filled = int(percent / 10)
    return "█" * filled + "░" * (10 - filled)

def extract_info(url, progress_callback, download=True):
    ydl_opts = {
        "quiet": True,
        "outtmpl": f"{BASE_DIR}/%(uploader)s/%(upload_date)s_%(title)s.%(ext)s",
        "merge_output_format": "mp4",
        "format": "bestvideo+bestaudio/best",
        "noplaylist": False,
        "ignoreerrors": True,
        "progress_hooks": [progress_callback]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=download)
    return info

def parse_metadata(info):
    return {
        "title": info.get("title"),
        "description": info.get("description"),
        "uploader": info.get("uploader"),
        "uploader_id": info.get("uploader_id"),
        "views": info.get("view_count") or 0,
        "likes": info.get("like_count") or 0,
        "comments": info.get("comment_count") or 0,
        "shares": info.get("repost_count") or 0,
        "duration": info.get("duration"),
        "upload_date": info.get("upload_date"),
        "platform": info.get("extractor"),
        "thumbnail": info.get("thumbnail"),
        "filename": info.get("_filename")
    }

def pass_filters(meta, filters):
    if not meta:
        return False
    if filters.get("min_views") and meta["views"] < filters["min_views"]:
        return False
    if filters.get("min_likes") and meta["likes"] < filters["min_likes"]:
        return False
    if filters.get("after_date"):
        try:
            video_date = datetime.strptime(meta["upload_date"], "%Y%m%d")
            if video_date < filters["after_date"]:
                return False
        except:
            pass
    if filters.get("before_date"):
        try:
            video_date = datetime.strptime(meta["upload_date"], "%Y%m%d")
            if video_date > filters["before_date"]:
                return False
        except:
            pass
    return True

def zip_folder(folder_path):
    zip_path = f"{folder_path}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)
    return zip_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 TikTok + Facebook Downloader Bot\n\n"
        "Fitur:\n"
        "✅ Download video / playlist / profile\n"
        "✅ Download semua video TikTok username\n"
        "✅ Download semua video Facebook Page\n"
        "✅ Filter by date / views / likes\n"
        "✅ Auto ZIP hasil\n"
        "✅ Kirim sebagai dokumen\n"
        "✅ Real-time progress\n\n"
        "Contoh:\n"
        "@username\n"
        "https://facebook.com/page\n"
        "/filter views=10000 after=2024-01-01\n"
    )

async def set_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters_data = {}
    for arg in context.args:
        if arg.startswith("views="):
            filters_data["min_views"] = int(arg.split("=")[1])
        elif arg.startswith("likes="):
            filters_data["min_likes"] = int(arg.split("=")[1])
        elif arg.startswith("after="):
            filters_data["after_date"] = dateparse(arg.split("=")[1])
        elif arg.startswith("before="):
            filters_data["before_date"] = dateparse(arg.split("=")[1])
    context.user_data["filters"] = filters_data
    await update.message.reply_text(f"✅ Filter diset: {filters_data}")

async def clear_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("filters", None)
    await update.message.reply_text("❌ Filter dihapus")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.startswith("@"):
        text = f"https://www.tiktok.com/{text}"
    progress_msg = await update.message.reply_text("⬇️ Starting download...")
    def progress_hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            if total:
                percent = downloaded / total * 100
                bar = progress_bar(percent)
                speed = d.get("speed", 0)
                eta = d.get("eta", 0)
                text = (
                    f"⬇️ Downloading...\n"
                    f"{bar} {percent:.1f}%\n"
                    f"⚡ {speed/1024/1024:.2f} MB/s\n"
                    f"⏳ ETA: {eta}s"
                )
                try:
                    context.application.create_task(progress_msg.edit_text(text))
                except:
                    pass
        elif d["status"] == "finished":
            try:
                context.application.create_task(progress_msg.edit_text("📦 Processing file..."))
            except:
                pass
    info = extract_info(text, progress_hook, download=True)
    filters_cfg = context.user_data.get("filters", {})
    files_sent = 0
    base_folder = None
    if "entries" in info:
        for entry in info["entries"]:
            if not entry:
                continue
            meta = parse_metadata(entry)
            if not pass_filters(meta, filters_cfg):
                continue
            base_folder = os.path.dirname(meta["filename"])
            files_sent += 1
    else:
        meta = parse_metadata(info)
        if pass_filters(meta, filters_cfg):
            base_folder = os.path.dirname(meta["filename"])
            files_sent = 1
    if not base_folder or files_sent == 0:
        return await update.message.reply_text("❌ Tidak ada video yang lolos filter")
    zip_path = zip_folder(base_folder)
    with open(zip_path, "rb") as f:
        await update.message.reply_document(document=InputFile(f), filename=os.path.basename(zip_path))
    shutil.rmtree(base_folder, ignore_errors=True)
    os.remove(zip_path)
    await progress_msg.edit_text(f"✅ Selesai — {files_sent} video dikirim dalam ZIP")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("filter", set_filter))
    app.add_handler(CommandHandler("clearfilter", clear_filter))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
