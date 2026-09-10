import os
import time
from threading import Thread
from flask import Flask
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ----------------- FLASK SERVER (Keeps Render port open) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot is Live! ✅"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, threaded=True)

# ----------------- GEMINI CLIENT -----------------
gemini_client = None
if os.getenv("GEMINI_API_KEY"):
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

WELCOME_TEXT = """
✨ **Welcome to the Lookup & AI Bot!** ✨

⚠️ **DISCLAIMER:**
This tool is strictly for Educational & Security Awareness purposes.
All data is indexed from publicly available data leaks.
We do not promote misuse, tracking, or illegal activities. Protect your privacy! 🛡️
"""

# ----------------- BOT HANDLERS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown")

# ----------------- MAIN -----------------
if __name__ == "__main__":
    # 1. Start Flask in a background thread first
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Small delay so the port binds properly
    time.sleep(2)

    # 2. Start Telegram Bot
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not BOT_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable is missing!")
        exit(1)

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    print("✅ Bot is starting...")
    application.run_polling(drop_pending_updates=True)
