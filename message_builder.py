"""بناء نصوص رسائل التحديث: رسالة صرف منفردة ورسالة ذهب منفردة"""
from datetime import datetime
from gold_price import get_gold_price_usd_per_ounce
from exchange_rate import (
    get_usd_yer_sanaa,
    get_usd_yer_aden,
    get_sar_yer_sanaa,
    get_sar_yer_aden,
)
from config import TROY_OUNCE_IN_GRAMS

DIVIDER = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"


def _fmt(n: float) -> str:
    return f"{n:,.0f}"


def _row(label: str, value: str, emoji: str = "▫️") -> str:
    return f"{emoji} {label}  ┃  *{value}*"


def _now_strings():
    now = datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")


def build_exchange_message() -> str:
    usd_sanaa = get_usd_yer_sanaa()["sell"]
    usd_aden = get_usd_yer_aden()["sell"]
    sar_sanaa = get_sar_yer_sanaa()["sell"]
    sar_aden = get_sar_yer_aden()["sell"]

    now_date, now_time = _now_strings()

    lines = []
    lines.append("💱✨ *تحديث أسعار الصرف* ✨💱")
    lines.append(DIVIDER)
    lines.append(f"📅 التاريخ: *{now_date}*      🕐 الوقت: *{now_time}*")
    lines.append(DIVIDER)
    lines.append("")
    lines.append("💵 *الدولار الأمريكي مقابل الريال اليمني*")
    lines.append(_row("صنعاء", f"{_fmt(usd_sanaa)} ريال", "🔹"))
    lines.append(_row("عدن", f"{_fmt(usd_aden)} ريال", "🔸"))
    lines.append("")
    lines.append(DIVIDER)
    lines.append("🇸🇦 *الريال السعودي مقابل الريال اليمني*")
    lines.append(_row("صنعاء", f"{_fmt(sar_sanaa)} ريال", "🔹"))
    lines.append(_row("عدن", f"{_fmt(sar_aden)} ريال", "🔸"))
    lines.append("")
    lines.append(DIVIDER)
    lines.append("🔗 قناتنا: t.me/priceGoldyemen")

    return "\n".join(lines)


def build_gold_message() -> str:
    ounce_usd = get_gold_price_usd_per_ounce()
    gram24_usd = ounce_usd / TROY_OUNCE_IN_GRAMS

    usd_sanaa = get_usd_yer_sanaa()["sell"]
    usd_aden = get_usd_yer_aden()["sell"]

    karats_usd = {
        "24": gram24_usd,
        "22": gram24_usd * 22 / 24,
        "21": gram24_usd * 21 / 24,
        "18": gram24_usd * 18 / 24,
    }

    now_date, now_time = _now_strings()

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
    lines.append("🔗 قناتنا: t.me/priceGoldyemen")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_exchange_message())
    print("\n\n" + "=" * 40 + "\n\n")
    print(build_gold_message())
