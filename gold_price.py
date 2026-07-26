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
