import requests

KLEVU_SEARCH_URL = "https://eucs25.ksearchnet.com/cs/v2/search"
KLEVU_KEY = "klevu-161710301480613427"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
}


def fetch_magic_madhouse():
    name = "Magic Madhouse"

    payload = {
        "context": {"apiKeys": [KLEVU_KEY]},
        "recordQueries": [
            {
                "id": "productList",
                "typeOfRequest": "SEARCH",
                "settings": {
                    "query": {"term": "palworld"},
                    "typeOfRecords": ["KLEVU_PRODUCT"],
                    "limit": "24",
                    "sort": "NEW_ARRIVAL_DESC",
                    "fallbackQueryId": "productListFallback",
                },
            }
        ],
    }

    r = requests.post(KLEVU_SEARCH_URL, headers=HEADERS, json=payload)
    r.raise_for_status()
    data = r.json()

    # find the "productList" result block
    records = []
    for query_result in data.get("queryResults", []):
        if query_result.get("id") == "productList":
            records = query_result.get("records", [])
            break

    products = []
    for rec in records:
        products.append({
            "name": rec.get("name"),
            "price": rec.get("salePrice") or rec.get("price"),
            "url": rec.get("url"),
            "in_stock": int(rec.get("inventory_level", 0) or 0) > 0,
        })

    return name, products


def main():
    name, products = fetch_magic_madhouse()

    print(f"\n{name} — found {len(products)} product(s):\n")
    for p in products:
        stock = "IN STOCK" if p["in_stock"] else "out of stock"
        print(f"  {p['name']}  |  £{p['price']}  |  {stock}")
        print(f"    {p['url']}")


if __name__ == "__main__":
    main()