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
