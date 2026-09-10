import os
import sys
import datetime
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ----------------- FLASK SERVER FOR RENDER PORT -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ----------------- GEMINI CLIENT SETUP -----------------
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
    await update.message.reply_text(WELCOME_TEXT)

# (Aap apne baki sare custom handlers yahan add kar sakte hain)

# ----------------- MAIN EXECUTION -----------------
if __name__ == '__main__':
    # 1. Start Flask in a background thread to keep Render port open
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # 2. Start Telegram Bot
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Run bot polling
    application.run_polling()
