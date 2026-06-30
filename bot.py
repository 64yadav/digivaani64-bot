"""
DigiVaani64 Telegram Bot
Services aur Courses dikhata hai, click karne pe website ka link bhejta hai.

Setup:
1. requirements.txt install karo: pip install -r requirements.txt
2. .env file banao aur BOT_TOKEN daalo (ya environment variable set karo)
3. python bot.py se run karo
"""

import os
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ── Logging setup (taaki errors terminal mein dikhe) ──
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── CONFIG: Yahan apni details daalo ──
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEBSITE_BASE = "https://64yadav.github.io/DigiVaani"
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "1790823274")  # Tera Telegram Chat ID — yahan notifications aayengi
CONTACT_PHONE = "+91 98765 43210"  # Apna real number daal de
CONTACT_WHATSAPP = "919876543210"  # Country code + number, bina + ya space (wa.me ke liye)
CONTACT_EMAIL = "hello@digivaani64.in"

# ── DATA: Services aur Courses (data.js jaisa hi, yahan bhi sync rakhna) ──
SERVICES = [
    {"id": "whatsapp-bot", "icon": "🤖", "title": "WhatsApp Bot", "desc": "Auto-reply, lead capture, order tracking — 24/7 automation."},
    {"id": "website-design", "icon": "🌐", "title": "Website Design", "desc": "Professional website — shop, clinic, coaching ke liye."},
    {"id": "data-dashboard", "icon": "📊", "title": "Data Dashboard", "desc": "Excel/Power BI mein business data clearly samjho."},
    {"id": "social-media", "icon": "📣", "title": "Social Media Setup", "desc": "Instagram, Facebook, Google My Business setup."},
    {"id": "database-solutions", "icon": "🗄️", "title": "Database Solutions", "desc": "Student records, inventory, billing system."},
    {"id": "digital-documents", "icon": "🖨️", "title": "Digital Documents", "desc": "Certificates, letterheads, invoices, presentations."},
]

COURSES = [
    {"id": "excel", "icon": "📊", "title": "MS Excel Mastery", "desc": "Formulas, Pivot Tables, MIS Reports — 20 hrs."},
    {"id": "sql", "icon": "🗃️", "title": "SQL for Data Analysis", "desc": "SELECT se JOINs tak — 15 hrs."},
    {"id": "web-design", "icon": "🌐", "title": "Web Design Basics", "desc": "HTML, CSS, JavaScript — 18 hrs."},
    {"id": "power-bi", "icon": "📈", "title": "Power BI Dashboard", "desc": "Data visualization & DAX — 12 hrs."},
    {"id": "python", "icon": "🐍", "title": "Python for Beginners", "desc": "Basics se automation tak — 22 hrs."},
    {"id": "ms-office", "icon": "💼", "title": "MS Office Complete", "desc": "Word, Excel, PowerPoint — 25 hrs."},
]


# ═══════════════════════════════════════
# REUSABLE MENU BUILDERS
# Inhe /start, /services, /courses commands AUR button clicks dono use karte hain
# — isse code duplicate nahi hota aur dono jagah same behavior milta hai.
# ═══════════════════════════════════════

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Services", callback_data="menu_services")],
        [InlineKeyboardButton("🎓 Skills / Courses", callback_data="menu_courses")],
        [InlineKeyboardButton("📞 Contact Us", callback_data="menu_contact")],
        [InlineKeyboardButton("🌐 Visit Website", url=WEBSITE_BASE)],
    ])


def main_menu_text():
    return (
        "Namaste! 🙏 DigiVaani64 mein aapka swagat hai.\n\n"
        "Hum digital services dete hain aur skill courses bhi sikhate hain.\n"
        "Neeche se option chuniye:"
    )


def services_menu_keyboard():
    keyboard = []
    for svc in SERVICES:
        keyboard.append([
            InlineKeyboardButton(f"{svc['icon']} {svc['title']}", callback_data=f"svc_{svc['id']}")
        ])
    keyboard.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)


def courses_menu_keyboard():
    keyboard = []
    for course in COURSES:
        keyboard.append([
            InlineKeyboardButton(f"{course['icon']} {course['title']}", callback_data=f"course_{course['id']}")
        ])
    keyboard.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)


def contact_text():
    return (
        "📞 Hume Contact Karo\n\n"
        f"📱 Phone: {CONTACT_PHONE}\n"
        f"📧 Email: {CONTACT_EMAIL}\n"
        f"💬 WhatsApp: wa.me/{CONTACT_WHATSAPP}\n\n"
        "Free consultation ke liye seedha message karo — hum jald hi reply karenge!"
    )


def contact_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 WhatsApp Pe Baat Karo", url=f"https://wa.me/{CONTACT_WHATSAPP}")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_main")],
    ])


# ═══════════════════════════════════════
# ADMIN NOTIFICATION HELPER
# Jab bhi koi user bot use kare ya kisi service/course me interest dikhaye,
# tujhe (admin) turant ek alert message Telegram pe aayega.
# ═══════════════════════════════════════
async def notify_admin(context: ContextTypes.DEFAULT_TYPE, user, message: str):
    """Admin ko Telegram pe notification bhejta hai (plain text — Markdown errors se bachne ke liye)."""
    try:
        username = f"@{user.username}" if user.username else "(no username)"
        full_name = user.full_name or "Unknown"
        text = (
            f"🔔 Naya Activity!\n\n"
            f"👤 Naam: {full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 User ID: {user.id}\n\n"
            f"📋 {message}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
    except Exception as e:
        logger.error(f"Admin notification failed: {e}")


# ═══════════════════════════════════════
# HANDLERS
# ═══════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab user /start bhejta hai ya pehli baar bot ko message karta hai."""
    await update.message.reply_text(main_menu_text(), reply_markup=main_menu_keyboard())

    # Admin ko notify karo ki naya user aaya
    await notify_admin(context, update.effective_user, "Bot ko /start kiya (naya ya returning user)")


async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab user /services bhejta hai — direct services list, /start ki zaroorat nahi."""
    await update.message.reply_text(
        "🤖 Hamari Services:\n\nKisi bhi service pe click karke details dekho.",
        reply_markup=services_menu_keyboard(),
    )


async def courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab user /courses bhejta hai — direct courses list, /start ki zaroorat nahi."""
    await update.message.reply_text(
        "🎓 Hamare Courses:\n\nKisi bhi course pe click karke syllabus dekho.",
        reply_markup=courses_menu_keyboard(),
    )


async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab user /contact bhejta hai — direct contact info."""
    await update.message.reply_text(contact_text(), reply_markup=contact_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab user kisi inline button pe click karta hai."""
    query = update.callback_query
    await query.answer()  # Telegram ko batata hai ki click receive hua

    data = query.data

    # ── Main menu: Services list dikhao ──
    if data == "menu_services":
        await query.edit_message_text(
            "🤖 Hamari Services:\n\nKisi bhi service pe click karke details dekho.",
            reply_markup=services_menu_keyboard(),
        )

    # ── Main menu: Courses list dikhao ──
    elif data == "menu_courses":
        await query.edit_message_text(
            "🎓 Hamare Courses:\n\nKisi bhi course pe click karke syllabus dekho.",
            reply_markup=courses_menu_keyboard(),
        )

    # ── Main menu: Contact info dikhao ──
    elif data == "menu_contact":
        await query.edit_message_text(contact_text(), reply_markup=contact_keyboard())

    # ── Back to main menu ──
    elif data == "back_main":
        await query.edit_message_text(main_menu_text(), reply_markup=main_menu_keyboard())

    # ── Specific service click — link bhejo ──
    elif data.startswith("svc_"):
        svc_id = data.replace("svc_", "")
        svc = next((s for s in SERVICES if s["id"] == svc_id), None)
        if svc:
            link = f"{WEBSITE_BASE}/service-detail.html?id={svc_id}"
            keyboard = [
                [InlineKeyboardButton("🔗 Full Details Dekho", url=link)],
                [InlineKeyboardButton("💬 WhatsApp Pe Pucho", url=f"https://wa.me/{CONTACT_WHATSAPP}")],
                [InlineKeyboardButton("⬅️ Back to Services", callback_data="menu_services")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                f"{svc['icon']} {svc['title']}\n\n{svc['desc']}\n\n"
                f"Puri details ke liye niche click karo:\n\n"
                f"Dhanyawad interest dikhane ke liye! 🙏 Hum jald hi aapse contact karenge."
            )
            await query.edit_message_text(text, reply_markup=reply_markup)

            # Admin ko notify karo — kisi service mein interest dikhaya
            await notify_admin(context, update.effective_user, f"Service mein interest dikhaya: {svc['title']}")

    # ── Specific course click — link bhejo ──
    elif data.startswith("course_"):
        course_id = data.replace("course_", "")
        course = next((c for c in COURSES if c["id"] == course_id), None)
        if course:
            link = f"{WEBSITE_BASE}/course-detail.html?id={course_id}"
            keyboard = [
                [InlineKeyboardButton("🔗 Full Syllabus Dekho", url=link)],
                [InlineKeyboardButton("💬 WhatsApp Pe Enroll Karo", url=f"https://wa.me/{CONTACT_WHATSAPP}")],
                [InlineKeyboardButton("⬅️ Back to Courses", callback_data="menu_courses")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                f"{course['icon']} {course['title']}\n\n{course['desc']}\n\n"
                f"Puri details ke liye niche click karo:\n\n"
                f"Dhanyawad interest dikhane ke liye! 🙏 Hum jald hi aapse contact karenge."
            )
            await query.edit_message_text(text, reply_markup=reply_markup)

            # Admin ko notify karo — kisi course mein interest dikhaya
            await notify_admin(context, update.effective_user, f"Course mein interest dikhaya: {course['title']}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab user /help bhejta hai."""
    await update.message.reply_text(
        "Bot use karna simple hai:\n\n"
        "/start - Main menu dekho\n"
        "/services - Seedha services list dekho\n"
        "/courses - Seedha courses list dekho\n"
        "/contact - Hume contact karo\n"
        "/help - Ye message dekho\n\n"
        "Bas buttons pe click karo aur explore karo! 🚀"
    )


# ═══════════════════════════════════════
# KEEP-ALIVE WEB SERVER (Render free tier ke liye zaruri)
# Render free "web service" ko ek open port chahiye, warna deploy fail hota hai.
# Ye chhota Flask server bas "I'm alive" bolta hai.
# ═══════════════════════════════════════
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "DigiVaani64 Bot is running! 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)


# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️  ERROR: BOT_TOKEN set nahi hai! .env file ya environment variable mein daalo.")
        return

    # Flask server ko background thread mein chalao (sirf Render health-check ke liye)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Bot ko MAIN thread mein chalao — isse event loop conflict nahi hota
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("services", services_command))
    app.add_handler(CommandHandler("courses", courses_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot start ho gaya! Telegram pe jaake test karo.")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
