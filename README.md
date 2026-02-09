# TikTok & Facebook Downloader Bot

Bot Telegram ini dapat digunakan untuk mengunduh video dari TikTok dan Facebook secara otomatis. Cukup kirimkan link video TikTok atau Facebook ke bot, dan bot akan mengunduh video tersebut tanpa watermark.

## Fitur:
- Auto-detect link TikTok atau Facebook
- Mengunduh video dengan kualitas terbaik (HD)
- Mendukung pengunduhan video TikTok berdasarkan username menggunakan command `/ttmass <username>`

## Cara Menjalankan:
1. Clone repository ini.
2. Install dependencies menggunakan `pip install -r requirements.txt`.
3. Daftarkan bot ke Telegram menggunakan BotFather dan masukkan token di file `bot.py`.
4. Jalankan bot menggunakan `python bot.py`.

## Deployment ke Railway:
1. Upload kode ke GitHub.
2. Deploy aplikasi ke Railway dengan mengikuti petunjuk di Railway.app.
3. Setel environment variable `TELEGRAM_BOT_TOKEN` dengan token yang diperoleh dari BotFather.