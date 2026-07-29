"""بوت تيليجرام لأسعار الذهب مقابل الدولار والريال اليمني"""
import asyncio
import logging
from datetime import time as dt_time

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN, CHAT_ID
from message_builder import build_exchange_message, build_gold_message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# مواعيد النشر بتوقيت UTC (9ص و5م بتوقيت اليمن UTC+3)
MORNING_UTC = dt_time(hour=6, minute=0)
EVENING_UTC = dt_time(hour=14, minute=0)


async def send_daily_update(context: ContextTypes.DEFAULT_TYPE):
    """ينشر رسالة الصرف ثم رسالة الذهب، كل واحدة منفصلة"""
    try:
        exchange_text = build_exchange_message()
        await context.bot.send_message(chat_id=CHAT_ID, text=exchange_text, parse_mode="Markdown", disable_web_page_preview=True)
        logger.info("تم نشر رسالة الصرف بنجاح")

        await asyncio.sleep(2)

        gold_text = build_gold_message()
        await context.bot.send_message(chat_id=CHAT_ID, text=gold_text, parse_mode="Markdown", disable_web_page_preview=True)
        logger.info("تم نشر رسالة الذهب بنجاح")
    except Exception as e:
        logger.exception("فشل نشر التحديث اليومي: %s", e)


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        exchange_text = build_exchange_message()
        await update.message.reply_text(exchange_text, parse_mode="Markdown", disable_web_page_preview=True)

        gold_text = build_gold_message()
        await update.message.reply_text(gold_text, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        logger.exception("فشل تنفيذ أمر /price: %s", e)
        await update.message.reply_text("⚠️ حدث خطأ أثناء جلب الأسعار، حاول مرة أخرى بعد قليل.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ أهلاً بك! 👋\n\n"
        "استخدم الأمر /price لمعرفة أسعار الصرف والذهب الحالية.\n"
        "كما أقوم بنشر تحديث تلقائي مرتين يوميًا (9 صباحًا و5 مساءً بتوقيت اليمن)."
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("price", price_command))

    job_queue = app.job_queue
    job_queue.run_daily(send_daily_update, time=MORNING_UTC, name="morning_update")
    job_queue.run_daily(send_daily_update, time=EVENING_UTC, name="evening_update")

    logger.info("🟡 البوت يعمل الآن...")
    app.run_polling()


if __name__ == "__main__":
    main()
