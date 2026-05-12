import os
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

logging.basicConfig(
format=”%(asctime)s - %(name)s - %(levelname)s - %(message)s”,
level=logging.INFO
)
logger = logging.getLogger(**name**)

BOT_TOKEN = os.environ.get(“BOT_TOKEN”, “”)

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
args = context.args

```
referrer_id = None
if args:
    try:
        referrer_id = int(args[0])
        if referrer_id == user.id:
            referrer_id = None
    except ValueError:
        referrer_id = None

is_new = db.register_user(
    user_id=user.id,
    username=user.username or "",
    full_name=user.full_name,
    referrer_id=referrer_id
)

if is_new and referrer_id:
    try:
        referrer = db.get_user(referrer_id)
        if referrer:
            count = db.get_referral_count(referrer_id)
            await context.bot.send_message(
                chat_id=referrer_id,
                text="<b>" + user.full_name + "</b> sizning havolangiz orqali qoshildi!\n"
                     "Sizning jami referrallaringiz: <b>" + str(count) + "</b> ta",
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error("Xato: " + str(e))

keyboard = [
    [InlineKeyboardButton("Mening referrallarim", callback_data="my_referrals")],
    [InlineKeyboardButton("Taklif havolam", callback_data="my_link")],
    [InlineKeyboardButton("Reyting", callback_data="top_referrers")],
]
reply_markup = InlineKeyboardMarkup(keyboard)

welcome_text = (
    "Salom, <b>" + user.full_name + "</b>!\n\n"
    "Bu bot orqali dostlaringizni taklif qiling va statistikangizni kuzating.\n\n"
    "Quyidagi bolimlardan birini tanlang:"
)

if update.message:
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")
else:
    await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")
```

async def my_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
user_id = query.from_user.id
referrals = db.get_referrals(user_id)
count = len(referrals)

if count == 0:
    text = "<b>Mening referrallarim</b>\n\nHali hech kim qoshilmagan.\nDostlaringizga havolangizni yuboring!"
else:
    text = "<b>Mening referrallarim</b> (" + str(count) + " ta)\n\n"
    for i, ref in enumerate(referrals, 1):
        name = ref["full_name"] or "Anonim"
        username = "@" + ref["username"] if ref["username"] else ""
        date = ref["joined_at"][:10]
        text += str(i) + ". " + name + " " + username + " - " + date + "\n"

keyboard = [[InlineKeyboardButton("Orqaga", callback_data="back_main")]]
await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
```

async def my_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
user_id = query.from_user.id
bot_username = (await context.bot.get_me()).username
referral_link = "https://t.me/" + bot_username + "?start=" + str(user_id)
count = db.get_referral_count(user_id)

text = (
    "<b>Sizning taklif havolangiz:</b>\n\n"
    "<code>" + referral_link + "</code>\n\n"
    "Siz orqali qoshilganlar: <b>" + str(count) + "</b> ta\n\n"
    "Ushbu havolani dostlaringizga yuboring!"
)

keyboard = [[InlineKeyboardButton("Orqaga", callback_data="back_main")]]
await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
```

async def top_referrers(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
top = db.get_top_referrers(limit=10)

if not top:
    text = "<b>Reyting</b>\n\nHali malumot yoq."
else:
    text = "<b>Top referralchilar</b>\n\n"
    for i, user in enumerate(top):
        medal = str(i+1) + "."
        name = user["full_name"] or "Anonim"
        username = "@" + user["username"] if user["username"] else ""
        count = user["referral_count"]
        text += medal + " " + name + " " + username + " - <b>" + str(count) + "</b> ta\n"

keyboard = [[InlineKeyboardButton("Orqaga", callback_data="back_main")]]
await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
```

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
ADMIN_ID = 1964705682

```
if update.effective_user.id != ADMIN_ID:
    await update.message.reply_text("Sizda ruxsat yoq.")
    return

total_users = db.get_total_users()
total_referrals = db.get_total_referrals()

text = (
    "<b>Umumiy statistika</b>\n\n"
    "Jami foydalanuvchilar: <b>" + str(total_users) + "</b>\n"
    "Referral orqali qoshilganlar: <b>" + str(total_referrals) + "</b>\n"
)
await update.message.reply_text(text, parse_mode="HTML")
```

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler(“start”, start))
app.add_handler(CommandHandler(“stats”, stats_command))
app.add_handler(CallbackQueryHandler(button_handler))
print(“Bot ishga tushdi!”)
app.run_polling(allowed_updates=Update.ALL_TYPES)

if **name** == “**main**”:
main()
