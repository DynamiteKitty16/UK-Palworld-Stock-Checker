# probShopifySites.py — scrapes The Card Vault, returns a list of products
import requests

SOURCE = "The Card Vault"
URL = "https://thecardvault.co.uk/collections/palworld-official-card-game-all-products/products.json?limit=250"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def fetch():
    """Returns (source_name, [products])."""
    r = requests.get(URL, headers=HEADERS, timeout=15)
    r.raise_for_status()

    products = []
    for p in r.json()["products"]:
        title = p["title"]

        # Safety net in case the collection URL ever changes
        if "palworld" not in title.lower():
            continue

        variants = p.get("variants", [])
        in_stock = any(v.get("available") for v in variants)
        price = variants[0]["price"] if variants else None

        products.append({
            "name": title,
            "price": price,
            "url": f"https://thecardvault.co.uk/products/{p['handle']}",
            "in_stock": in_stock,
        })

    return SOURCE, products