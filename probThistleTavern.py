# probThistleTavern.py — Thistle Tavern (Shopify) via search suggest API.
# The /collections/palworld page is an empty "Coming Soon" placeholder and the
# rapid-search page is JS-rendered, so we hit Shopify's search suggest JSON,
# which returns published products (incl. pre-orders) matching the query.
import requests

SOURCE = "Thistle Tavern"
BASE = "https://thistletavern.com"
URL = (
    f"{BASE}/search/suggest.json"
    "?q=palworld&resources[type]=product&resources[limit]=25"
)

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def fetch():
    """Returns (source_name, [products])."""
    r = requests.get(URL, headers=HEADERS, timeout=15)
    r.raise_for_status()

    items = r.json()["resources"]["results"]["products"]

    products = []
    for p in items:
        title = p["title"]

        # Essential: search returns fuzzy matches (e.g. a VaultX binder),
        # so keep only genuine Palworld products.
        if "palworld" not in title.lower():
            continue

        # suggest.json gives a relative url + product-level 'available'
        url = p.get("url", "")
        if url.startswith("/"):
            url = BASE + url

        products.append({
            "name": title,
            "price": p.get("price"),
            "url": url,
            "in_stock": bool(p.get("available")),
        })

    return SOURCE, products