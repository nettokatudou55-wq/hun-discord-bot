import os
import time
import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

TARGET_FC = "3441-9881-1452"  # 監視するフレンドコード
CHECK_INTERVAL = 5            # 5秒ごとにチェック
COOLDOWN = 6 * 60 * 60        # 6時間（秒換算）

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_notify_time = 0  # 最後に通知した時間（UNIX時間）

@bot.event
async def on_ready():
    print(f"ログイン完了: {bot.user}")
    check_status.start()

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_status():
    global last_notify_time

    try:
        # チャンネルを確実に取得
        channel = await bot.fetch_channel(CHANNEL_ID)

        # Wiimmfi のページを取得
        url = "https://wiimmfi.de/stats/mkw"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        # フレンドコードがオンラインか確認
        online = soup.find(string=TARGET_FC)

        if online:
            now = time.time()

            # クールダウン中なら通知しない
            if now - last_notify_time < COOLDOWN:
                return

            # 通知
            await channel.send("ふんさん発生！！")

            # 通知時間を更新
            last_notify_time = now

    except Exception as e:
        print("エラー:", e)

bot.run(TOKEN)

