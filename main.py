import os
import asyncio
import re
import requests
import sqlite3
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice
)
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    ContextTypes,
    filters
)

# ==========================================
# CONFIGURATION (SECURE VIA ENVIRONMENT VARIABLES)
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "https://anurixx-gift-number.vercel.app/api?num=")

# Admin Details
ADMIN_EMAIL = "webcyber.online@gmail.com"
ADMIN_CHAT_ID = 2053552882

# ==========================================
# ADVERTISEMENT CONTENT
# ==========================================

AD_TEXT = (
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "🔞 **NOTICE:** Yah sirf 18+ saal ke logo ke liye hai. "
    "Jinki skills acchi ho wahi khelein.\n\n"
    "🚀 **AB HAR MATCH MEIN HOGA BADA DHAMAKA!** 🤑😎🤘💥\n"
    "• Best Betting Line (No Lag)\n"
    "• Instant ID Generation\n"
    "• 24/7 Deposit & Withdrawal\n"
    "• Cricket, Football &\n"
    "Rules simple hain: Limit mein khelo, jeet ke niklo! 🤑💰\n\n"
    "👉 ID ke liye contact: @hanbot30\n"
    "━━━━━━━━━━━━━━━━━━━━━"
)


# ==========================================
# DATABASE LOGIC
# ==========================================

def init_db():
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            trial_end TIMESTAMP,
            premium_end TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def register_user(user_id):
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        trial_end = datetime.now() + timedelta(days=7)  # 7 Days Free Trial
        cursor.execute(
            'INSERT INTO users (user_id, trial_end, premium_end) VALUES (?, ?, ?)',
            (user_id, trial_end.isoformat(), None)
        )
        conn.commit()
    conn.close()

def is_user_premium(user_id):
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT trial_end, premium_end FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False
        
    now = datetime.now()
    trial_end = datetime.fromisoformat(row[0]) if row[0] else None
    premium_end = datetime.fromisoformat(row[1]) if row[1] else None
    
    if trial_end and now < trial_end:
        return True
    if premium_end and now < premium_end:
        return True
        
    return False

def add_premium_days(user_id, days):
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT premium_end FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    now = datetime.now()
    current_expiry = datetime.fromisoformat(row[0]) if row and row[0] else now
    start_date = max(now, current_expiry)
    new_expiry = start_date + timedelta(days=days)
    
    cursor.execute(
        'UPDATE users SET premium_end = ? WHERE user_id = ?',
        (new_expiry.isoformat(), user_id)
    )
    conn.commit()
    conn.close()


# ==========================================
# COMMAND HANDLERS
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id)

    welcome_text = (
        f"👋 Welcome, {user.first_name}!\n\n"
        "🎉 You have received a 7-Day Free Trial.\n\n"
        "🔎 Send any phone number to look up information.\n"
        "💳 Use the /buy command to view subscription plans.\n"
        "📩 Send suggestions using /suggest <your message>"
    )

    try:
        photos = await context.bot.get_user_profile_photos(
            user_id=user.id,
            limit=1
        )

        if photos.total_count > 0:
            photo_id = photos.photos[0][-1].file_id
            await update.message.reply_photo(photo=photo_id, caption=welcome_text)
        else:
            await update.message.reply_text(welcome_text)

    except Exception:
        await update.message.reply_text(welcome_text)


async def suggest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    suggestion_text = " ".join(context.args)

    if not suggestion_text:
        await update.message.reply_text(
            "📝 **How to send a suggestion:**\n"
            "Format: `/suggest Your feedback or suggestion message`\n\n"
            f"📧 Direct Support Email: `{ADMIN_EMAIL}`\n"
            "👤 Admin: @webcyber_online",
            parse_mode="Markdown"
        )
        return

    username_display = f"@{user.username}" if user.username else "No Username"

    admin_notification = (
        f"📩 **New Suggestion Received!**\n\n"
        f"👤 **From:** {user.first_name} ({username_display})\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"💬 **Message:** {suggestion_text}"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_notification,
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Thank you! Your suggestion has been delivered to the admin.")
    except Exception:
        await update.message.reply_text(
            f"✅ Thank you! If you need direct support, reach us at: `{ADMIN_EMAIL}`",
            parse_mode="Markdown"
        )


# ==========================================
# NUMBER LOOKUP
# ==========================================

async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_user_premium(user_id):
        buy_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ 1 Month Plan (100 Stars)", callback_data="buy_1m")],
            [InlineKeyboardButton("⭐ 3 Month Plan (250 Stars)", callback_data="buy_3m")],
            [InlineKeyboardButton("⭐ 1 Year Plan (800 Stars)", callback_data="buy_1y")]
        ])
        await update.message.reply_text(
            "❌ **Your 7-Day Free Trial Has Expired!**\n\n"
            "Please select a subscription plan below to continue using the service:\n"
            "Command: /buy",
            parse_mode="Markdown",
            reply_markup=buy_keyboard
        )
        return

    number = update.message.text.strip()
    clean_number = re.sub(r"[^\d+]", "", number)

    if not clean_number:
        await update.message.reply_text("❌ Please send a valid phone number.")
        return

    searching_message = await update.message.reply_text(
        "🔎 Searching...\n\n⏳ Please wait..."
    )

    try:
        response = requests.get(API_URL + clean_number, timeout=30)
        response.raise_for_status()
        api_data = response.json()

        results = api_data.get("Results", [])
        if not results:
            await searching_message.edit_text("❌ No results found.")
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

        lines.append(AD_TEXT)

        result_text = "\n".join(lines)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Delete (1 min)", callback_data="delete_result")]
        ])

        await searching_message.edit_text(
            result_text, 
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

        await asyncio.sleep(60)
        try:
            await searching_message.delete()
        except Exception:
            pass

    except requests.exceptions.Timeout:
        try:
            await searching_message.edit_text("❌ Request timed out. Please try again.")
        except Exception:
            pass
    except requests.exceptions.RequestException:
        try:
            await searching_message.edit_text("❌ Server connection failed. Please try again later.")
        except Exception:
            pass
    except Exception as error:
        print("ERROR:", error)
        try:
            await searching_message.edit_text("❌ Something went wrong.")
        except Exception:
            pass


# ==========================================
# SUBSCRIPTION & PAYMENTS
# ==========================================

async def show_plans(chat_id, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐ 1 Month Plan (100 Stars)", callback_data="buy_1m")],
        [InlineKeyboardButton("⭐ 3 Month Plan (250 Stars)", callback_data="buy_3m")],
        [InlineKeyboardButton("⭐ 1 Year Plan (800 Stars)", callback_data="buy_1y")]
    ])
    await context.bot.send_message(
        chat_id=chat_id,
        text="💳 **Choose a Subscription Plan:**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_plans(update.effective_chat.id, context)

async def plan_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_data = {
        "buy_1m": {"title": "1 Month Premium Subscription", "days": 30, "stars": 100},
        "buy_3m": {"title": "3 Months Premium Subscription", "days": 90, "stars": 250},
        "buy_1y": {"title": "1 Year Premium Subscription", "days": 365, "stars": 800},
    }

    selected = plan_data.get(query.data)
    if not selected:
        return

    payload = f"PLAN_{selected['days']}"
    prices = [LabeledPrice(selected["title"], selected["stars"])]

    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=selected["title"],
        description=f"Unlock unlimited lookups for {selected['days']} days.",
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=prices
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if not query.invoice_payload.startswith("PLAN_"):
        await query.answer(ok=False, error_message="Payment verification failed.")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    payload = update.message.successful_payment.invoice_payload
    
    days = int(payload.split("_")[1])
    add_premium_days(user_id, days=days)
    
    await update.message.reply_text(
        f"🎉 **Payment Successful!**\n\nYour Premium Subscription has been activated for {days} days.",
        parse_mode="Markdown"
    )


# ==========================================
# DELETE RESULT BUTTON
# ==========================================

async def delete_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🗑 Deleted successfully!")
    try:
        await query.message.delete()
    except Exception:
        pass


# ==========================================
# MAIN APPLICATION
# ==========================================

def main():
    init_db()

    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN not found in Environment Variables!")
        return

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

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy_command))
    app.add_handler(CommandHandler("suggest", suggest_command))

    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    app.add_handler(CallbackQueryHandler(delete_result, pattern="^delete_result$"))
    app.add_handler(CallbackQueryHandler(plan_selection_callback, pattern="^buy_(1m|3m|1y)$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup))

    print("================================")
    print("🤖 BOT STARTED SUCCESSFULLY")
    print("================================")

    app.run_polling()


if __name__ == "__main__":
    main()
