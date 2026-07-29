"""جلب أسعار صرف الدولار والريال السعودي مقابل الريال اليمني من exrye.com"""
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


def _parse_currency_row(html: str, keywords: list) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue
            row_text = row.get_text(" ", strip=True)
            if any(k in row_text for k in keywords):
                numbers = []
                for cell in cells:
                    text = cell.get_text(strip=True).replace(",", "")
                    try:
                        numbers.append(float(text))
                    except ValueError:
                        continue
                if len(numbers) >= 2:
                    return {"buy": numbers[0], "sell": numbers[1]}

    raise ValueError(f"لم يتم العثور على صف يطابق {keywords} - قد يكون شكل الصفحة تغيّر")


def _fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text


def get_usd_yer_sanaa() -> dict:
    html = _fetch(YER_SANAA_URL)
    return _parse_currency_row(html, ["USD", "الدولار"])


def get_usd_yer_aden() -> dict:
    html = _fetch(YER_ADEN_URL)
    return _parse_currency_row(html, ["USD", "الدولار"])


def get_sar_yer_sanaa() -> dict:
    html = _fetch(YER_SANAA_URL)
    return _parse_currency_row(html, ["SAR", "سعودي"])


def get_sar_yer_aden() -> dict:
    html = _fetch(YER_ADEN_URL)
    return _parse_currency_row(html, ["SAR", "سعودي"])


if __name__ == "__main__":
    print("دولار صنعاء:", get_usd_yer_sanaa())
    print("دولار عدن:", get_usd_yer_aden())
    print("سعودي صنعاء:", get_sar_yer_sanaa())
    print("سعودي عدن:", get_sar_yer_aden())
