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
