import discord
import asyncio
import requests
from bs4 import BeautifulSoup
import time
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

TARGET_FC = "3441-9881-1452"
CHECK_INTERVAL = 5
COOLDOWN = 8 * 60 * 60

last_notify_time = 0

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def is_online():
    url = "https://wiimmfi.de/stats/mkw"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tr")
    for row in rows:
        cols = row.text.strip()
        if TARGET_FC in cols:
            if "online" in cols.lower():
                return True
    return False

async def monitor_status():
    global last_notify_time
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while True:
        try:
            online = is_online()
            now = time.time()
            if online and (now - last_notify_time > COOLDOWN):
                await channel.send("ふんさん発生！！")
                last_notify_time = now
        except Exception as e:
            print("Error:", e)
        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    print(f"ログイン完了: {client.user}")
    client.loop.create_task(monitor_status())

client.run(TOKEN)
