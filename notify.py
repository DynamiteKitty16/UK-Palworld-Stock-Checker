# notify.py — the ONLY file that talks to Discord
import os
import requests

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
DISCORD_USER_ID = os.environ.get("DISCORD_USER_ID")  # optional, for @pinging you


def send(message, ping=False):
    """Send a message to Discord. Set ping=True to @mention you."""
    if ping and DISCORD_USER_ID:
        content = f"<@{DISCORD_USER_ID}> {message}"
    else:
        content = message

    print("DISCORD:", message)
    requests.post(DISCORD_WEBHOOK, json={"content": content}, timeout=15)