import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
IMAGE_PATHS = ["image.png", "image.jpg", "image.jpeg"]  # Görseli bu isimlerden biriyle botun yanına koy
IMAGE_URL = os.getenv("IMAGE_URL", "")  # image.png yoksa bu link kullanılır
STATUS_NAME = "Comolokko"  # Botun altında "Comolokko izliyor" olarak görünür

MESSAGE_TEXT = """https://www.tiktok.com/@comolokko.46
https://www.instagram.com/hturk46
https://kick.com/comolokko-46

https://www.tiktok.com/@raiwennxd
https://kick.com/raiwennxd"""


# ---------- Render için küçük web sunucusu ----------
# Render "Web Service" bir port görmek ister. Bu sunucu sadece "Bot calisiyor"
# yazar, böylece Render servisi "Live" yapar. UptimeRobot buraya ping atarak
# servisin uyumasını engelleyebilir.
class _Saglik(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot calisiyor")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


def _web_baslat():
    port = int(os.getenv("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), _Saglik).serve_forever()


threading.Thread(target=_web_baslat, daemon=True).start()


def build_message():
    """Embed'i ve (varsa) görsel dosyasını hazırlar."""
    embed = discord.Embed(description=MESSAGE_TEXT, color=0x0A0A0C)
    file = None

    found = next((p for p in IMAGE_PATHS if os.path.exists(p)), None)
    if found:
        file = discord.File(found, filename=found)
        embed.set_image(url=f"attachment://{found}")
    elif IMAGE_URL:
        embed.set_image(url=IMAGE_URL)

    return embed, file


class Bot(discord.Client):
    def __init__(self):
        super().__init__(
            intents=discord.Intents.default(),
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=STATUS_NAME
            ),
        )
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = Bot()


@bot.tree.command(name="sosyal", description="Sosyal medya linklerini gönderir")
async def sosyal(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed, file = build_message()
    if file:
        await interaction.channel.send(embed=embed, file=file)
    else:
        await interaction.channel.send(embed=embed)
    await interaction.delete_original_response()


@bot.event
async def on_ready():
    print(f"Giriş yapıldı: {bot.user}")


bot.run(TOKEN)