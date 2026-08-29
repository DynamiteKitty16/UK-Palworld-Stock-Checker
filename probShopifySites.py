# probShopifySites.py
import requests, json, os

URL = "https://thecardvault.co.uk/collections/palworld-official-card-game-all-products/products.json?limit=250"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
WATCH_KEYWORDS = ["set 02", "set 2", "legends awaken"]
STATE_FILE = "seen.json"
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
DISCORD_USER_ID = os.environ.get("DISCORD_USER_ID")  # for pinging me in alerts, if set

# --- Toggles (read from environment variables set by the workflow) ---
TEST_MODE  = os.environ.get("TEST_MODE") == "1"
HEARTBEAT  = os.environ.get("HEARTBEAT") == "1"
MANUAL_RUN = os.environ.get("MANUAL_RUN") == "1"


def get_products():
    r = requests.get(URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()["products"]


def is_watched(title):
    return any(w in title.lower() for w in WATCH_KEYWORDS)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"known_handles": [], "stock": {}}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def alert(message, ping=True):
    print("ALERT:", message)
    if ping and DISCORD_USER_ID:
        content = f"<@{DISCORD_USER_ID}> {message}"
    else:
        content = message
    requests.post(DISCORD_WEBHOOK, json={"content": content})


def check():
    state = load_state()
    products = get_products()
    current = []
    watched_in_stock = []

    for p in products:
        handle, title = p["handle"], p["title"]
        current.append(handle)

        if handle not in state["known_handles"] and state["known_handles"]:
            alert(f"NEW PRODUCT: {title}\nhttps://thecardvault.co.uk/products/{handle}")

        if is_watched(title):
            in_stock = any(v["available"] for v in p["variants"])
            if in_stock:
                watched_in_stock.append(title)
            if in_stock and not state["stock"].get(handle, False):
                alert(f"BACK IN STOCK: {title}\nhttps://thecardvault.co.uk/products/{handle}")
            state["stock"][handle] = in_stock

    state["known_handles"] = current
    save_state(state)
    print(f"Checked {len(products)} products.")

    # Report back on daily heartbeat OR whenever you run it manually
    if HEARTBEAT or MANUAL_RUN:
        if watched_in_stock:
            items = "\n".join(f"• {t}" for t in watched_in_stock)
            alert(f"✅ Checked {len(products)} products — these watched items are IN STOCK:\n{items}")
        else:
            alert(f"✅ Checked {len(products)} products — nothing watched is in stock right now! 😴", ping=False)


if TEST_MODE:
    alert("🧪 TEST: This is what a stock alert looks like! Webhook is working. 🎉")
else:
    check()