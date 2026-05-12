import sqlite3
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# =========================
# TOKEN
# =========================
BOT_TOKEN = "8407362693:AAG8sBcu4U2REOVUsEXNVwANSGcpZsjBgRg"

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("referral.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    username TEXT,
    referrer_id INTEGER
)
""")

conn.commit()

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    args = context.args

    referrer_id = None

    if args:
        try:
            referrer_id = int(args[0])

            if referrer_id == user.id:
                referrer_id = None

        except:
            referrer_id = None

    # user mavjudmi
    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user.id,)
    )

    existing_user = cursor.fetchone()

    # yangi user
    if not existing_user:

        cursor.execute(
            """
            INSERT INTO users
            (user_id, full_name, username, referrer_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                user.id,
                user.full_name,
                user.username,
                referrer_id
            )
        )

        conn.commit()

        # referral xabari
        if referrer_id:

            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE referrer_id = ?",
                (referrer_id,)
            )

            count = cursor.fetchone()[0]

            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=(
                        f"🎉 <b>{user.full_name}</b> "
                        f"sizning havolangiz orqali qo‘shildi!\n\n"
                        f"📊 Jami referral: <b>{count}</b> ta"
                    ),
                    parse_mode="HTML"
                )

            except Exception as e:
                logger.error(e)

    # menu
    keyboard = [
        [
            InlineKeyboardButton(
                "👥 Referrallarim",
                callback_data="refs"
            )
        ],
        [
            InlineKeyboardButton(
                "🔗 Taklif linkim",
                callback_data="link"
            )
        ],
        [
            InlineKeyboardButton(
                "🏆 Reyting",
                callback_data="top"
            )
        ]
    ]

    text = (
        f"Salom <b>{user.full_name}</b> 👋\n\n"
        "Do‘stlaringizni taklif qiling "
        "va referral yig‘ing."
    )

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

# =========================
# BUTTONS
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # =====================
    # REFERRALS
    # =====================
    if query.data == "refs":

        cursor.execute(
            """
            SELECT full_name, username
            FROM users
            WHERE referrer_id = ?
            """,
            (user_id,)
        )

        refs = cursor.fetchall()

        if not refs:

            text = "❌ Sizda referral yo‘q."

        else:

            text = f"👥 Referrallar: {len(refs)} ta\n\n"

            for i, ref in enumerate(refs, start==1):

                name = ref[0]
                username = ref[1]

                if username:
                    text += f"{i}. {name} (@{username})\n"
                else:
                    text += f"{i}. {name}\n"

        keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ Orqaga",
                    callback_data="back"
                )
            ]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # =====================
    # LINK
    # =====================
    elif query.data == "link":

        bot = await context.bot.get_me()

        link = f"https://t.me/{bot.username}?start={user_id}"

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE referrer_id = ?",
            (user_id,)
        )

        count = cursor.fetchone()[0]

        text = (
            "🔗 Sizning taklif havolangiz:\n\n"
            f"{link}\n\n"
            f"👥 Referral: {count} ta"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ Orqaga",
                    callback_data="back"
                )
            ]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # =====================
    # TOP
    # =====================
    elif query.data == "top":

        cursor.execute("""
        SELECT full_name, username, COUNT(*) as total
        FROM users
        WHERE referrer_id IS NOT NULL
        GROUP BY referrer_id
        ORDER BY total DESC
        LIMIT 10
        """)

        top_users = cursor.fetchall()

        if not top_users:

            text = "❌ Reyting bo‘sh."

        else:

            text = "🏆 TOP REFERRALCHILAR\n\n"

            for i, user in enumerate(top_users, start==1):

                name = user[0]
                username = user[1]
                total = user[2]

                if username:
                    text += f"{i}. {name} (@{username}) - {total}\n"
                else:
                    text += f"{i}. {name} - {total}\n"

        keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ Orqaga",
                    callback_data="back"
                )
            ]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # =====================
    # BACK
    # =====================
    elif query.data == "back":

        keyboard = [
            [
                InlineKeyboardButton(
                    "👥 Referrallarim",
                    callback_data="refs"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔗 Taklif linkim",
                    callback_data="link"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏆 Reyting",
                    callback_data="top"
                )
            ]
        ]

        text = (
            f"Salom <b>{query.from_user.full_name}</b> 👋\n\n"
            "Menu:"
        )

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

# =========================
# MAIN
# =========================
def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(buttons)
    )

    print("✅ Bot ishga tushdi!")

    app.run_polling()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
