"""بوت تيليجرام لأسعار الذهب مقابل الدولار والريال اليمني"""
import logging
from datetime import time as dt_time

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN, CHAT_ID, DAILY_HOUR, DAILY_MINUTE
from message_builder import build_update_message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def send_daily_update(context: ContextTypes.DEFAULT_TYPE):
    try:
        text = build_update_message()
        await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")
        logger.info("تم نشر التحديث اليومي بنجاح")
    except Exception as e:
        logger.exception("فشل نشر التحديث اليومي: %s", e)


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = build_update_message()
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.exception("فشل تنفيذ أمر /price: %s", e)
        await update.message.reply_text("⚠️ حدث خطأ أثناء جلب الأسعار، حاول مرة أخرى بعد قليل.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ أهلاً بك! 👋\n\n"
        "استخدم الأمر /price لمعرفة سعر الذهب الحالي مقابل الدولار والريال اليمني.\n"
        "كما أقوم بنشر تحديث تلقائي يوميًا في وقت محدد."
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("price", price_command))

    job_queue = app.job_queue
    job_queue.run_daily(send_daily_update, time=dt_time(hour=DAILY_HOUR, minute=DAILY_MINUTE))

    logger.info("🟡 البوت يعمل الآن...")
    app.run_polling()


if __name__ == "__main__":
    main()
