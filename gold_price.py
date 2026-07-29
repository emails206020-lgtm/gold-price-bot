"""جلب سعر الذهب العالمي من gold-api.com + بيع/شراء عيار 21 والجنيه من boqash.com"""
import re
import requests
from bs4 import BeautifulSoup
from config import GOLD_API_URL, TROY_OUNCE_IN_GRAMS, KARATS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

BOQASH_GOLD_URL = "https://boqash.com/prices-gold/"


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


def _clean_number(text: str):
    match = re.search(r"[\d,]+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0).replace(",", ""))


def get_local_gold_buy_sell() -> dict:
    """
    يجلب بيع/شراء لعيار 21 والجنيه في صنعاء وعدن من boqash.com
    البنية المتوقعة للصف: [النوع, المدينة, شراء, بيع, التاريخ]
    """
    resp = requests.get(BOQASH_GOLD_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tables = soup.find_all("table")
    result = {
        "sanaa": {"21": None, "pound": None},
        "aden": {"21": None, "pound": None},
    }
    seen = set()

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            # الخلية الأولى = النوع (عيار21/جنيه)، الثانية = المدينة
            type_text = cells[0].get_text(" ", strip=True)
            city_text = cells[1].get_text(" ", strip=True)

            is_pound = "جنيه" in type_text
            is_21 = "21" in type_text
            is_sanaa = "صنعاء" in city_text
            is_aden = "عدن" in city_text

            if not (is_pound or is_21) or not (is_sanaa or is_aden):
                continue

            city = "sanaa" if is_sanaa else "aden"
            kind = "pound" if is_pound else "21"
            key = (city, kind)
            if key in seen:
                continue

            # الأرقام فقط من الخلية الثالثة (شراء) والرابعة (بيع) فصاعدًا
            numbers = [_clean_number(c.get_text(strip=True)) for c in cells[2:]]
            numbers = [n for n in numbers if n is not None]
            if len(numbers) >= 2:
                result[city][kind] = {"buy": numbers[0], "sell": numbers[1]}
                seen.add(key)

    return result


if __name__ == "__main__":
    ounce = get_gold_price_usd_per_ounce()
    print(f"سعر الأونصة العالمي: {ounce:.2f} USD")
    for k in ["24", "22", "21", "18"]:
        print(f"جرام عيار {k} (سعر واحد): {get_gold_price_per_gram(k):.2f} USD")

    print("\n--- بيع/شراء محلي (boqash.com) ---")
    local = get_local_gold_buy_sell()
    print(local)
