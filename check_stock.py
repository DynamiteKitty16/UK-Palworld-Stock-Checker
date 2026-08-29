# check_stock.py — runs every scraper, tracks state, and sends alerts
import os
import json

import notify
import probShopifySites
import probScrapeSites
import probUnicornCards
import probThistleTavern

STATE_FILE = "seen.json"

TEST_MODE  = os.environ.get("TEST_MODE") == "1"
HEARTBEAT  = os.environ.get("HEARTBEAT") == "1"
MANUAL_RUN = os.environ.get("MANUAL_RUN") == "1"

# Add more scrapers to this list in future — that's the only change needed!
SITES = [probShopifySites, probScrapeSites, probUnicornCards, probThistleTavern]


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"known": [], "stock": {}}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def key(source, product):
    # Unique ID for each product across all sites
    return f"{source}::{product['url']}"


def main():
    if TEST_MODE:
        notify.send("🧪 TEST: This is what a stock alert looks like! Webhook is working. 🎉")
        return

    state = load_state()
    known = set(state.get("known", []))
    stock = state.get("stock", {})

    total = 0
    in_stock_now = []  # list of (source, name, url)

    for site in SITES:
        try:
            source, products = site.fetch()
        except Exception as e:
            notify.send(f"⚠️ Error checking {getattr(site, 'SOURCE', site.__name__)}: {e}", ping=True)
            continue

        for p in products:
            total += 1
            k = key(source, p)

            # New product (only announce once we've already seen this site before)
            if k not in known and known:
                notify.send(f"🆕 NEW at {source}: [{p['name']}]({p['url']})")

            if p["in_stock"]:
                in_stock_now.append((source, p["name"], p["url"], p["price"]))
                # Only alert if it WASN'T in stock last time
                if not stock.get(k, False):
                    notify.send(
                        f"🔔 BACK IN STOCK at {source}: [{p['name']}]({p['url']}) — £{p['price']}",
                        ping=True,
                    )

            stock[k] = p["in_stock"]
            known.add(k)

    state["known"] = sorted(known)
    state["stock"] = stock
    save_state(state)
    print(f"Checked {total} products across {len(SITES)} site(s).")

    # Heartbeat / manual summary (silent — no ping)
    if HEARTBEAT or MANUAL_RUN:
        if in_stock_now:
            lines = "\n".join(
                f"• **{s}** — [{n}]({u}) — £{pr}" for s, n, u, pr in in_stock_now
            )
            notify.send(
                f"✅ Checked {total} products — these Palworld items are IN STOCK:\n{lines}",
                ping=False,
            )
        else:
            notify.send(
                f"✅ Checked {total} products — nothing is in stock right now! 😴",
                ping=False,
            )


if __name__ == "__main__":
    main()