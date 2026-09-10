import os
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Gemini Client Setup
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Fixed Welcome Text (Clean Markdown)
WELCOME_TEXT = """
👋 *Welcome to the Bot!*

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

👉 Send a *Number* for Lookup or type any *Question* to chat with AI!
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Lookup logic for numbers
    if text.isdigit():
        await update.message.reply_text(f"🔍 Searching lookup details for: {text}...")
    
    # AI Chatbot logic for normal text/questions
    else:
        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=text,
            )
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text("Maaf kijiye, abhi AI response nahi de pa raha hai.")

def main():
    bot_token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(bot_token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 BOT STARTED SUCCESSFULLY")
    app.run_polling()

if __name__ == "__main__":
    main()
