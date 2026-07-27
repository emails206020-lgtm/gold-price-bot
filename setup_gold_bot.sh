#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🟡 بدء إعداد بوت أسعار الذهب..."
echo ""

# ---------- 1. تثبيت الحزم ----------
echo "📦 [1/6] تحديث وتثبيت الحزم الأساسية..."
pkg update -y -q && pkg upgrade -y -q
pkg install -y -q python git clang libxml2 libxslt libjpeg-turbo

# ---------- 2. إنشاء مجلد المشروع ----------
echo "📁 [2/6] إنشاء مجلد المشروع..."
mkdir -p ~/gold-price-bot-local
cd ~/gold-price-bot-local

# ---------- 3. إنشاء ملفات المشروع ----------
echo "🛠️  [3/6] إنشاء ملفات الكود..."

cat > config.py << 'EOF'
"""
إعدادات البوت - نسخة Termux محلية
كل القيم الحساسة تُقرأ من ملف .env
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN غير موجود! أضفه في ملف .env")
if not CHAT_ID:
    raise RuntimeError("CHAT_ID غير موجود! أضفه في ملف .env")

DAILY_HOUR = int(os.getenv("DAILY_HOUR", 9))
DAILY_MINUTE = int(os.getenv("DAILY_MINUTE", 0))

GOLD_API_URL = "https://api.gold-api.com/price/XAU"
YER_SANAA_URL = "https://exrye.com/sanaa"
YER_ADEN_URL = "https://exrye.com/aden"

TROY_OUNCE_IN_GRAMS = 31.1034768

KARATS = {
    "24": 24 / 24,
    "22": 22 / 24,
    "21": 21 / 24,
    "18": 18 / 24,
}
EOF

cat > gold_price.py << 'EOF'
"""جلب سعر الذهب بالدولار من gold-api.com (مجاني بدون مفتاح)"""
import requests
from config import GOLD_API_URL, TROY_OUNCE_IN_GRAMS, KARATS


def get_gold_price_usd_per_ounce() -> float:
    resp = requests.get(GOLD_API_URL, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return float(data["price"])


def get_gold_price_per_gram(karat: str = "24") -> float:
    price_per_ounce = get_gold_price_usd_per_ounce()
    price_per_gram_24k = price_per_ounce / TROY_OUNCE_IN_GRAMS
    factor = KARATS.get(karat, 1.0)
    return price_per_gram_24k * factor


if __name__ == "__main__":
    ounce = get_gold_price_usd_per_ounce()
    print(f"سعر الأونصة: {ounce:.2f} USD")
    for k in ["24", "22", "21", "18"]:
        print(f"جرام عيار {k}: {get_gold_price_per_gram(k):.2f} USD")
EOF

cat > exchange_rate.py << 'EOF'
"""جلب سعر صرف الدولار مقابل الريال اليمني من exrye.com"""
import requests
from bs4 import BeautifulSoup
from config import YER_SANAA_URL, YER_ADEN_URL

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _parse_usd_row(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue
            row_text = row.get_text(" ", strip=True)
            if "USD" in row_text or "الدولار" in row_text:
                numbers = []
                for cell in cells:
                    text = cell.get_text(strip=True).replace(",", "")
                    try:
                        numbers.append(float(text))
                    except ValueError:
                        continue
                if len(numbers) >= 2:
                    return {"buy": numbers[0], "sell": numbers[1]}

    raise ValueError("لم يتم العثور على صف الدولار - قد يكون شكل الصفحة تغيّر")


def get_usd_yer_sanaa() -> dict:
    resp = requests.get(YER_SANAA_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return _parse_usd_row(resp.text)


def get_usd_yer_aden() -> dict:
    resp = requests.get(YER_ADEN_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return _parse_usd_row(resp.text)


if __name__ == "__main__":
    print("صنعاء:", get_usd_yer_sanaa())
    print("عدن:", get_usd_yer_aden())
EOF

cat > message_builder.py << 'EOF'
"""بناء نص رسالة تحديث الأسعار بتصميم احترافي منسق"""
from datetime import datetime
from gold_price import get_gold_price_usd_per_ounce
from exchange_rate import get_usd_yer_sanaa, get_usd_yer_aden
from config import TROY_OUNCE_IN_GRAMS

DIVIDER = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"


def _fmt(n: float) -> str:
    return f"{n:,.0f}"


def _row(label: str, value: str, emoji: str = "▫️") -> str:
    return f"{emoji} {label}  ┃  *{value}*"


def build_update_message() -> str:
    ounce_usd = get_gold_price_usd_per_ounce()
    gram24_usd = ounce_usd / TROY_OUNCE_IN_GRAMS

    sanaa = get_usd_yer_sanaa()
    aden = get_usd_yer_aden()

    usd_sanaa = sanaa["sell"]
    usd_aden = aden["sell"]

    karats_usd = {
        "24": gram24_usd,
        "22": gram24_usd * 22 / 24,
        "21": gram24_usd * 21 / 24,
        "18": gram24_usd * 18 / 24,
    }

    now_date = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")

    lines = []
    lines.append("✨🟡 *تحديث أسعار الذهب* 🟡✨")
    lines.append(DIVIDER)
    lines.append(f"📅 التاريخ: *{now_date}*      🕐 الوقت: *{now_time}*")
    lines.append(DIVIDER)
    lines.append("")
    lines.append("💰 *سعر الأونصة العالمي (XAU/USD)*")
    lines.append(f"┃  *{ounce_usd:,.2f} $*")
    lines.append("")
    lines.append(DIVIDER)
    lines.append("💵 *سعر صرف الدولار مقابل الريال اليمني*")
    lines.append(_row("صنعاء", f"{_fmt(usd_sanaa)} ريال", "🔹"))
    lines.append(_row("عدن", f"{_fmt(usd_aden)} ريال", "🔸"))
    lines.append("")
    lines.append(DIVIDER)
    lines.append("📊 *سعر جرام الذهب بالدولار*")
    for k, v in karats_usd.items():
        lines.append(_row(f"عيار {k}", f"{v:,.2f} $"))
    lines.append("")
    lines.append(DIVIDER)
    lines.append("🇾🇪 *سعر جرام الذهب بالريال اليمني — صنعاء*")
    for k, v in karats_usd.items():
        lines.append(_row(f"عيار {k}", f"{_fmt(v * usd_sanaa)} ريال", "🔹"))
    lines.append("")
    lines.append("🇾🇪 *سعر جرام الذهب بالريال اليمني — عدن*")
    for k, v in karats_usd.items():
        lines.append(_row(f"عيار {k}", f"{_fmt(v * usd_aden)} ريال", "🔸"))
    lines.append("")
    lines.append(DIVIDER)
    lines.append("🔗 المصدر: gold-api.com | exrye.com")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_update_message())
EOF

cat > bot.py << 'EOF'
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
EOF

cat > requirements.txt << 'EOF'
python-telegram-bot[job-queue]==21.4
requests==2.32.3
beautifulsoup4==4.12.3
python-dotenv==1.0.1
EOF

cat > .env << 'EOF'
BOT_TOKEN=ضع_توكن_البوت_هنا
CHAT_ID=-1003382641647
DAILY_HOUR=9
DAILY_MINUTE=0
EOF

echo "📚 [4/6] تثبيت مكتبات Python..."
pip install -r requirements.txt -q

echo "🔧 [5/6] لا حاجة لـ git في النسخة المحلية"

echo ""
echo "✅ [6/6] تم إعداد المشروع المحلي في: ~/gold-price-bot-local"
echo ""
echo "════════════════════════════════════════"
echo "📋 الخطوة الأخيرة عليك:"
echo "════════════════════════════════════════"
echo ""
echo "1️⃣  عدّل التوكن في ملف .env:"
echo "    cd ~/gold-price-bot-local && nano .env"
echo "    (CHAT_ID موجود مسبقًا: -1003382641647)"
echo ""
echo "2️⃣  شغّل البوت:"
echo "    python bot.py"
echo ""
echo "════════════════════════════════════════"
