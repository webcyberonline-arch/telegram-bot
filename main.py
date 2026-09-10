import asyncio
import os
import re
from threading import Thread
import requests
from flask import Flask

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ==========================================
# KEEP ALIVE WEB SERVER (For Render 24/7)
# ==========================================

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is active and running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()


# ==========================================
# CONFIG
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# API Base URL (Agar endpoint me query format alag hai toh yahan replace kar lena)
API_URL = os.getenv("API_URL", "https://vercel.app/")


# ==========================================
# START
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    welcome_text = (
        "👋 Welcome to the Lookup\n\n"
        "1️⃣ ⚠️ DISCLAIMER:\n"
        "This tool is strictly for Educational & Security Awareness purposes.\n"
        "All data is indexed from publicly available data leaks.\n"
        "We do not promote misuse, tracking, or illegal activities. Protect your privacy! 🔒\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "2️⃣ 🚀 AB HAR MATCH MEIN HOGA BADA DHAMAKA! 🤑😎🤘💥\n"
        "⚡ Best Betting Line (No Lag)\n"
        "🆔 Instant ID Generation\n"
        "💸 24/7 Deposit & Withdrawal\n"
        "🏏 Cricket, Football & More\n"
        "📌 Rules simple hain: Limit mein khelo, jeet ke niklo! 🤑💰\n"
        "📲 ID ke liye Contact: @hanbot30\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👉 Send a 10-digit number"
    )

    try:
        photos = await context.bot.get_user_profile_photos(
            user_id=user.id,
            limit=1
        )

        if photos.total_count > 0:
            photo_id = photos.photos[0][-1].file_id

            await update.message.reply_photo(
                photo=photo_id,
                caption=welcome_text
            )
        else:
            await update.message.reply_text(welcome_text)

    except Exception:
        await update.message.reply_text(welcome_text)


# ==========================================
# NUMBER LOOKUP
# ==========================================

async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()

    # Keep only digits and '+' character
    clean_number = re.sub(r"[^\d+]", "", number)

    if not clean_number:
        await update.message.reply_text(
            "❌ Please send a valid number."
        )
        return

    searching_message = await update.message.reply_text(
        "🔎 Searching...\n\n"
        "⏳ Please wait..."
    )

    try:
        # API Request construct
        target_url = f"{API_URL}{clean_number}" if API_URL.endswith("/") else f"{API_URL}/{clean_number}"
        
        response = requests.get(
            target_url,
            timeout=30
        )

        response.raise_for_status()
        api_data = response.json()

        results = api_data.get("Results", [])
        if not results:
            await searching_message.edit_text(
                "❌ No results found."
            )
            return

        lines = [
            "╭━━━━━━━━━━━━━━━━━━━━╮",
            "       🔎 NUMBER RESULT",
            "╰━━━━━━━━━━━━━━━━━━━━╯\n"
        ]

        for idx, entry in enumerate(results, start=1):
            lines.append(f"📌 Result #{idx}")
            lines.append(f"• Mobile : {entry.get('mobile', 'N/A')}")
            lines.append(f"• Name   : {entry.get('name', 'N/A')}")
            lines.append(f"• Father : {entry.get('fname', 'N/A')}")
            lines.append(f"• Address: {entry.get('address', 'N/A')}")
            lines.append(f"• Alt No : {entry.get('alt', 'N/A')}")
            lines.append(f"• Circle : {entry.get('circle', 'N/A')}")
            lines.append(f"• ID     : {entry.get('id', 'N/A')}")
            lines.append(f"• Email  : {entry.get('email', 'Not Available')}")
            lines.append("")

        # Display note from API response
        note = api_data.get("note")
        if note:
            lines.append(f"📝 Note: {note}")

        result_text = "\n".join(lines)

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🗑 Delete in 1 Minute",
                    callback_data="delete_result"
                )
            ]
        ])

        await searching_message.edit_text(
            result_text,
            reply_markup=keyboard
        )

        await asyncio.sleep(60)

        try:
            await searching_message.delete()
        except Exception:
            pass

    except requests.exceptions.Timeout:
        try:
            await searching_message.edit_text(
                "❌ API request timeout.\n\n"
                "Please try again."
            )
        except Exception:
            pass

    except requests.exceptions.RequestException:
        try:
            await searching_message.edit_text(
                "❌ API connection failed.\n\n"
                "Please try again later."
            )
        except Exception:
            pass

    except ValueError:
        try:
            await searching_message.edit_text(
                "❌ API provided an invalid response."
            )
        except Exception:
            pass

    except Exception as error:
        print("ERROR:", error)

        try:
            await searching_message.edit_text(
                "❌ Something went wrong."
            )
        except Exception:
            pass


# ==========================================
# DELETE BUTTON
# ==========================================

async def delete_result(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer("🗑 Deleted successfully!")

    try:
        await query.message.delete()
    except Exception:
        pass


# ==========================================
# MAIN
# ==========================================

def main():
    # Starts the background Flask server
    keep_alive()

    telegram_request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=60,
        write_timeout=60,
        pool_timeout=60
    )

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(telegram_request)
        .get_updates_request(telegram_request)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            lookup
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            delete_result,
            pattern="^delete_result$"
        )
    )

    print("================================")
    print("🤖 BOT STARTED")
    print("================================")

    app.run_polling()


if __name__ == "__main__":
    main()
