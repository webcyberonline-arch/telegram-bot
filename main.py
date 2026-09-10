import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from google import genai

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------- FLASK APP -----------------
app = Flask(__name__)

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

# ----------------- TELEGRAM APPLICATION -----------------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN environment variable is missing!")

application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# ----------------- FLASK ROUTES -----------------
@app.route('/')
def home():
    return "Telegram Bot is Live! ✅", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Telegram will send updates here"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK", 200

# ----------------- STARTUP -----------------
async def setup_webhook():
    """Set webhook when the app starts"""
    webhook_url = os.getenv("WEBHOOK_URL")  # e.g. https://telegram-bot-hn0b.onrender.com/webhook
    
    if webhook_url:
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook set to: {webhook_url}")
    else:
        logger.warning("⚠️ WEBHOOK_URL not set. Webhook not configured.")

# Initialize application
import asyncio

async def main():
    await application.initialize()
    await setup_webhook()
    await application.start()

# Run the async setup
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
