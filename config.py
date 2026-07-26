"""
إعدادات البوت
كل القيم الحساسة تُقرأ من متغيرات البيئة (Railway -> Variables)
أو من ملف .env محليًا في Termux
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN غير موجود! أضفه في ملف .env أو متغيرات Railway")
if not CHAT_ID:
    raise RuntimeError("CHAT_ID غير موجود! أضفه في ملف .env أو متغيرات Railway")

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
