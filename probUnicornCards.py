# probUnicornCards.py — scrapes Unicorn Cards (Listock platform) via HTML
import requests
from bs4 import BeautifulSoup

SOURCE = "Unicorn Cards"
BASE = "https://unicorncards.co.uk"
SEARCH_URL = f"{BASE}/search?viewmode=grid&orderby=0&pagesize=96&q=palworld&advs=false"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
}


def fetch():
    """Returns (source_name, [products])."""
    r = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    products = []
    for card in soup.select("div.product-item"):
        link = card.select_one("a.product-title__link")
        if not link:
            continue

        name = link.get_text(strip=True)
        href = link.get("href", "")
        url = href if href.startswith("http") else BASE + href

        # Price: e.g. "£49.90" -> "49.90"  (may be missing on some cards)
        price_el = card.select_one("span.actual-price") or card.select_one("span.price")
        price = ""
        if price_el:
            price = price_el.get_text(strip=True).replace("£", "").strip()

        # Stock: OOS items carry the "product-item-out-of-stock" class
        classes = card.get("class", [])
        in_stock = "product-item-out-of-stock" not in classes

        products.append({
            "name": name,
            "price": price,
            "url": url,
            "in_stock": in_stock,
        })

    return SOURCE, products