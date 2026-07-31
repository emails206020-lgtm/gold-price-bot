"""بناء نصوص رسائل التحديث: رسالة صرف منفردة ورسالة ذهب منفردة"""
from datetime import datetime
from gold_price import get_gold_price_usd_per_ounce, get_local_gold_buy_sell
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


def _buy_sell_row(label: str, data: dict, emoji: str = "▫️") -> str:
    return f"{emoji} {label}  ┃  شراء: *{_fmt(data['buy'])}*  |  بيع: *{_fmt(data['sell'])}* ريال"


def _now_strings():
    now = datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")


def build_exchange_message() -> str:
    usd_sanaa = get_usd_yer_sanaa()
    usd_aden = get_usd_yer_aden()
    sar_sanaa = get_sar_yer_sanaa()
    sar_aden = get_sar_yer_aden()

    now_date, now_time = _now_strings()

    lines = []
    lines.append("💱✨ *تحديث أسعار الصرف* ✨💱")
    lines.append(DIVIDER)
    lines.append(f"📅 التاريخ: *{now_date}*      🕐 الوقت: *{now_time}*")
    lines.append(DIVIDER)
    lines.append("")
    lines.append("💵 *الدولار الأمريكي مقابل الريال اليمني*")
    lines.append(_buy_sell_row("صنعاء", usd_sanaa, "🔹"))
    lines.append(_buy_sell_row("عدن", usd_aden, "🔸"))
    lines.append("")
    lines.append(DIVIDER)
    lines.append("🇸🇦 *الريال السعودي مقابل الريال اليمني*")
    lines.append(_buy_sell_row("صنعاء", sar_sanaa, "🔹"))
    lines.append(_buy_sell_row("عدن", sar_aden, "🔸"))
    lines.append("")
    lines.append(DIVIDER)
    lines.append("🔗 قناتنا: t.me/priceGoldyemen")

    return "\n".join(lines)


def _gold_table(karats_data: dict, unit_label: str) -> str:
    rows = []
    for k, v in karats_data.items():
        value_str = f"{v:,.2f}" if isinstance(v, float) and v < 1000 else f"{v:,.0f}"
        rows.append(f"عيار {k:>2}  │  {value_str:>12} {unit_label}")
    table = "\n".join(rows)
    return f"```\n{table}\n```"


def _local_table(sanaa: dict, aden: dict) -> str:
    def line(label, s_data, a_data):
        s_buy = f"{s_data['buy']:,.0f}" if s_data else "—"
        s_sell = f"{s_data['sell']:,.0f}" if s_data else "—"
        a_buy = f"{a_data['buy']:,.0f}" if a_data else "—"
        a_sell = f"{a_data['sell']:,.0f}" if a_data else "—"
        return (
            f"{label:<8}│ صنعاء: {s_buy:>9} / {s_sell:>9}\n"
            f"{'':<8}│ عدن:   {a_buy:>9} / {a_sell:>9}"
        )

    rows = [
        "        (شراء / بيع بالريال)",
        line("عيار 21", sanaa["21"], aden["21"]),
        "",
        line("الجنيه", sanaa["pound"], aden["pound"]),
    ]
    table = "\n".join(rows)
    return f"```\n{table}\n```"


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
    karats_yer_sanaa = {k: v * usd_sanaa for k, v in karats_usd.items()}
    karats_yer_aden = {k: v * usd_aden for k, v in karats_usd.items()}

    now_date, now_time = _now_strings()

    lines = []
    lines.append("┏━━━━━━━━━━━━━━━━━━┓")
    lines.append("┃   🟡 *أسعار الذهب*   ┃")
    lines.append("┗━━━━━━━━━━━━━━━━━━┛")
    lines.append(f"📅 *{now_date}*   🕐 *{now_time}*")
    lines.append("")
    lines.append(f"💰 الأونصة العالمية (XAU/USD)")
    lines.append(f"    ➤  *{ounce_usd:,.2f} $*")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append("📊 *سعر الجرام بالدولار*")
    lines.append(_gold_table(karats_usd, "$"))

    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🇾🇪 *سعر الجرام بالريال — صنعاء*")
    lines.append(_gold_table(karats_yer_sanaa, "ريال"))

    lines.append("🇾🇪 *سعر الجرام بالريال — عدن*")
    lines.append(_gold_table(karats_yer_aden, "ريال"))

    try:
        local = get_local_gold_buy_sell()
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        lines.append("💎 *أسعار السوق المحلي*")
        lines.append("_(عيار 21 والجنيه — شراء / بيع)_")
        lines.append(_local_table(local["sanaa"], local["aden"]))
    except Exception:
        pass

    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🔗 قناتنا: t.me/priceGoldyemen")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_exchange_message())
    print("\n\n" + "=" * 40 + "\n\n")
    print(build_gold_message())
