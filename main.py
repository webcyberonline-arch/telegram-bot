import os
import re
import sqlite3
import requests
from datetime import datetime, timedelta
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Initialize Gemini AI Client using Environment Variable
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Welcome Message with Disclaimer and Promotional Banner
WELCOME_TEXT = """
👋 *Welcome to the Lookup & AI Bot!*

1️⃣ ⚠️ *DISCLAIMER:*
This tool is strictly for Educational & Security Awareness purposes.
All data is indexed from publicly available data leaks.
We do not promote misuse, tracking, or illegal activities. Protect your privacy! 🔒

━━━━━━━━━━━━━━━━━━━━━

2️⃣ 🚀 *AB HAR MATCH MEIN HOGA BADA DHAMAKA!* 🤑😎🤘💥
⚡ Best Betting Line (No Lag)
🆔 Instant ID Generation
💸 24/7 Deposit & Withdrawal
🏏 Cricket, Football & More
📌 *Rules simple hain: Limit mein khelo, jeet ke niklo!* 🤑💰
📲 *ID ke liye Contact:* @hanbot30
━━━━━━━━━━━━━━━━━━━━━

👉 Send a *10-digit number* for Lookup or ask any *Question* to chat with AI!
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and sends the welcome message."""
    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user input, separating phone lookup queries from general AI chat."""
    text = update.message.text.strip()
    
    # Check if user input is a 10-digit mobile number
    if re.match(r'^\d{10}$', text):
        await update.message.reply_text(f"🔍 Searching lookup details for: `{text}`...", parse_mode="Markdown")
        # Place your custom database or API lookup logic here
    else:
        # Route general queries to Gemini AI Chatbot
        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=text,
            )
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text("Sorry, there was an issue processing your AI response.")

def main():
    """Main function to initialize and start the Telegram bot application."""
    bot_token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(bot_token).build()
    
    # Register command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 BOT STARTED SUCCESSFULLY")
    app.run_polling()

if __name__ == "__main__":
    main()
