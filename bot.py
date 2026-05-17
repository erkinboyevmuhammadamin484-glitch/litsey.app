import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
WEB_APP_URL = "https://litsey-app.vercel.app"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🎓 Ilovani ochish",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Salom! Litsey Tayyorgarlik ilovasiga xush kelibsiz!\n\n"
        "📚 Bu ilova orqali:\n"
        "• Ingliz tili va matematika testlari ishlang\n"
        "• 1 oylik dars rejasini kuzating\n"
        "• Reytingda o'z o'rningizni biling\n\n"
        "⬇️ Ilovani ochish uchun tugmani bosing:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Yordam:\n\n"
        "/start - Ilovani ochish\n"
        "/help - Yordam\n\n"
        "🌐 To'g'ridan link: https://litsey-app.vercel.app"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
