import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
Application,
CommandHandler,
CallbackQueryHandler,
ContextTypes,
MessageHandler,
filters,
)
from database import Database

# Logging sozlash

logging.basicConfig(
format=”%(asctime)s - %(name)s - %(levelname)s - %(message)s”,
level=logging.INFO
)
logger = logging.getLogger(**name**)

import os

# Token Railway Variables dan olinadi

BOT_TOKEN = os.environ.get(“BOT_TOKEN”, “”)

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Botni ishga tushirish va referral tekshirish”””
user = update.effective_user
args = context.args  # referral link argumenti

```
referrer_id = None
if args:
    try:
        referrer_id = int(args[0])
        # O'z-o'zini qo'shishni oldini olish
        if referrer_id == user.id:
            referrer_id = None
    except ValueError:
        referrer_id = None

# Foydalanuvchini ro'yxatdan o'tkazish
is_new = db.register_user(
    user_id=user.id,
    username=user.username or "",
    full_name=user.full_name,
    referrer_id=referrer_id
)

if is_new and referrer_id:
    # Taklif qiluvchiga xabar yuborish
    try:
        referrer = db.get_user(referrer_id)
        if referrer:
            await context.bot.send_message(
                chat_id=referrer_id,
                text=f"🎉 <b>{user.full_name}</b> sizning havolangiz orqali qo'shildi!\n"
                     f"Sizning jami referrallaringiz: <b>{db.get_referral_count(referrer_id)}</b> ta",
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Referrer ga xabar yuborishda xato: {e}")

# Asosiy menyu
keyboard = [
    [InlineKeyboardButton("👥 Mening referrallarim", callback_data="my_referrals")],
    [InlineKeyboardButton("🔗 Taklif havolam", callback_data="my_link")],
    [InlineKeyboardButton("🏆 Reyting", callback_data="top_referrers")],
]
reply_markup = InlineKeyboardMarkup(keyboard)

welcome_text = (
    f"Salom, <b>{user.full_name}</b>! 👋\n\n"
    f"Bu bot orqali do'stlaringizni taklif qiling va statistikangizni kuzating.\n\n"
    f"Quyidagi bo'limlardan birini tanlang:"
)

if update.message:
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")
else:
    await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")
```

async def my_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Foydalanuvchi qo’shgan odamlar ro’yxati”””
query = update.callback_query
await query.answer()

```
user_id = query.from_user.id
referrals = db.get_referrals(user_id)
count = len(referrals)

if count == 0:
    text = (
        "👥 <b>Mening referrallarim</b>\n\n"
        "Hali hech kim qo'shilmagan.\n"
        "Do'stlaringizga havolangizni yuboring! 🔗"
    )
else:
    text = f"👥 <b>Mening referrallarim</b> ({count} ta)\n\n"
    for i, ref in enumerate(referrals, 1):
        name = ref['full_name'] or "Anonim"
        username = f"@{ref['username']}" if ref['username'] else ""
        date = ref['joined_at'][:10]  # Faqat sana
        text += f"{i}. {name} {username} — {date}\n"

keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]]
await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
```

async def my_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Foydalanuvchining referral havolasi”””
query = update.callback_query
await query.answer()

```
user_id = query.from_user.id
bot_username = (await context.bot.get_me()).username
referral_link = f"https://t.me/{bot_username}?start={user_id}"
count = db.get_referral_count(user_id)

text = (
    f"🔗 <b>Sizning taklif havolangiz:</b>\n\n"
    f"<code>{referral_link}</code>\n\n"
    f"📊 Siz orqali qo'shilganlar: <b>{count}</b> ta\n\n"
    f"Ushbu havolani do'stlaringizga yuboring!"
)

keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]]
await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
```

async def top_referrers(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Top referralchilar reytingi”””
query = update.callback_query
await query.answer()

```
top = db.get_top_referrers(limit=10)

if not top:
    text = "🏆 <b>Reyting</b>\n\nHali ma'lumot yo'q."
else:
    text = "🏆 <b>Top referralchilar</b>\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        name = user['full_name'] or "Anonim"
        username = f"@{user['username']}" if user['username'] else ""
        count = user['referral_count']
        text += f"{medal} {name} {username} — <b>{count}</b> ta\n"

keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]]
await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
```

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Admin uchun umumiy statistika”””
# Admin ID sini o’zgartiring
ADMIN_ID = 1964705682

```
if update.effective_user.id != ADMIN_ID:
    await update.message.reply_text("❌ Sizda ruxsat yo'q.")
    return

total_users = db.get_total_users()
total_referrals = db.get_total_referrals()

text = (
    f"📊 <b>Umumiy statistika</b>\n\n"
    f"👤 Jami foydalanuvchilar: <b>{total_users}</b>\n"
    f"🔗 Referral orqali qo'shilganlar: <b>{total_referrals}</b>\n"
)
await update.message.reply_text(text, parse_mode="HTML")
```

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Barcha tugmalar uchun handler”””
query = update.callback_query
data = query.data

```
if data == "my_referrals":
    await my_referrals(update, context)
elif data == "my_link":
    await my_link(update, context)
elif data == "top_referrers":
    await top_referrers(update, context)
elif data == "back_main":
    await start(update, context)
```

def main():
“”“Botni ishga tushirish”””
app = Application.builder().token(BOT_TOKEN).build()

```
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats_command))
app.add_handler(CallbackQueryHandler(button_handler))

print("✅ Bot ishga tushdi!")
app.run_polling(allowed_updates=Update.ALL_TYPES)
```

if **name** == “**main**”:
main()