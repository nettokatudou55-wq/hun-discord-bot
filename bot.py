
import discord
import asyncio
import requests
from bs4 import BeautifulSoup
import time
import os

# ====== 環境変数の取得 ======
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 値チェック（RailwayでNoneなら即クラッシュするので防止）
if TOKEN is None:
    raise ValueError("環境変数 TOKEN が設定されていません。Railway の Variables に TOKEN を追加してください。")

if CHANNEL_ID is None:
    raise ValueError("環境変数 CHANNEL_ID が設定されていません。Railway の Variables に CHANNEL_ID を追加してください。")

CHANNEL_ID = int(CHANNEL_ID)

# ====== 設定 ======
TARGET_FC = "3441-9881-1452"
CHECK_INTERVAL = 5
COOLDOWN = 8 * 60 * 60

last_notify_time = 0

# ====== Discord クライアント ======
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ====== Wiimmfi チェック関数 ======
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

# ====== 監視ループ ======
async def monitor_status():
    global last_notify_time
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("チャンネルが見つかりません。CHANNEL_ID が正しいか確認してください。")
        return

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

# ====== 起動時イベント ======
@client.event
async def on_ready():
    print(f"ログイン完了: {client.user}")
    client.loop.create_task(monitor_status())

# ====== 実行 ======
client.run(TOKEN)