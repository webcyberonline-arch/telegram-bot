import os
import logging
from flask import Flask, request, render_template_string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- BOT TOKEN ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") # https://tera-app.onrender.com/webhook

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN missing hai!")

# --- VOTE BOARD (Memory me) ---
votes = {"Option A": 0, "Option B": 0}

# --- TELEGRAM APP ---
application = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Live hai! Vote ke liye /vote likho")

async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        choice = " ".join(context.args)
        if choice in votes:
            votes[choice] += 1
            await update.message.reply_text(f"✅ {choice} ko vote mil gaya!")
        else:
            await update.message.reply_text(f"Options: {', '.join(votes.keys())}")
    else:
        await update.message.reply_text("Use: /vote Option A")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("vote", vote))

# --- FLASK ROUTES ---
@app.route('/')
def home():
    return "Bot Live 24/7 ✅", 200

@app.route('/board')
def board():
    html = f"""
    <html><head><title>Live Vote</title></head>
    <body style="font-family:sans-serif; text-align:center; margin-top:50px;">
    <h1>📊 Live Voting Board</h1>
    <h2>Option A: {votes['Option A']} votes</h2>
    <h2>Option B: {votes['Option B']} votes</h2>
    <p>Auto refresh in 3 sec</p>
    <script>setTimeout(()=>location.reload(),3000)</script>
    </body></html>
    """
    return render_template_string(html)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        # Render safe async handle
        asyncio.run(application.process_update(update))
        return "OK", 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return "Error", 500

# --- WEBHOOK SETUP ---
async def setup():
    await application.initialize()
    if WEBHOOK_URL:
        await application.bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"Webhook set to {WEBHOOK_URL}")

asyncio.run(setup())
