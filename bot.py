import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import pytz
import schedule
import threading
import time

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
OPENSEA_API_KEY = os.getenv("OPENSEA_API_KEY")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# OpenSea API endpoints
OPENSEA_API_BASE = "https://api.opensea.io/api/v2"

# Global variables
scheduler_thread = None


def get_recent_mints():
    """Fetch recent NFT mints from OpenSea"""
    try:
        headers = {
            "X-API-KEY": OPENSEA_API_KEY,
            "Accept": "application/json"
        }
        
        # Get recent collections (newly created)
        url = f"{OPENSEA_API_BASE}/collections"
        params = {
            "limit": 5,
            "order_by": "created_date",
            "order_direction": "desc"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("collections", [])
        else:
            print(f"Error fetching from OpenSea: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching mints: {e}")
        return []


def format_mint_embed(collection):
    """Format collection data as Discord embed"""
    try:
        embed = discord.Embed(
            title=collection.get("name", "Unknown Collection"),
            description=collection.get("description", "No description available")[:300],
            color=discord.Color.blue(),
            timestamp=datetime.now(pytz.UTC)
        )
        
        # Add collection image
        image_url = collection.get("image_url")
        if image_url:
            embed.set_thumbnail(url=image_url)
        
        # Add relevant fields
        embed.add_field(
            name="Creator",
            value=collection.get("creator", {}).get("user", {}).get("username", "Unknown"),
            inline=True
        )
        
        contract_address = collection.get("contracts", [{}])[0].get("address", "N/A")
        embed.add_field(
            name="Contract",
            value=f"`{contract_address[:10]}...`",
            inline=True
        )
        
        # Add OpenSea link
        opensea_url = collection.get("opensea_url", "#")
        embed.add_field(
            name="View on OpenSea",
            value=f"[Click here]({opensea_url})",
            inline=False
        )
        
        embed.set_footer(text="🌿 Daily Mint Bot")
        
        return embed
    except Exception as e:
        print(f"Error formatting embed: {e}")
        return None


async def post_daily_mints():
    """Post daily mints to the designated channel"""
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print(f"Channel {CHANNEL_ID} not found!")
            return
        
        # Fetch mints
        mints = get_recent_mints()
        
        if not mints:
            embed = discord.Embed(
                title="Daily Mint Update",
                description="No new mints found today. Check back later!",
                color=discord.Color.greyple(),
                timestamp=datetime.now(pytz.UTC)
            )
            await channel.send(embed=embed)
            return
        
        # Send embed for each mint
        embed = discord.Embed(
            title="🌿 Daily NFT Mints",
            description=f"Today's hottest new collections ({len(mints)} found)",
            color=discord.Color.gold(),
            timestamp=datetime.now(pytz.UTC)
        )
        embed.set_footer(text="Powered by OpenSea API")
        
        await channel.send(embed=embed)
        
        for mint in mints[:5]:  # Post top 5 mints
            mint_embed = format_mint_embed(mint)
            if mint_embed:
                await channel.send(embed=mint_embed)
                time.sleep(0.5)  # Small delay between messages
        
        print(f"Posted {len(mints)} mints to channel {CHANNEL_ID}")
    except Exception as e:
        print(f"Error posting daily mints: {e}")


def schedule_mints():
    """Schedule daily mints posting at 9:00 AM UTC"""
    schedule.every().day.at("09:00").do(lambda: bot.loop.create_task(post_daily_mints()))
    
    while True:
        schedule.run_pending()
        time.sleep(60)


@bot.event
async def on_ready():
    """Bot ready event"""
    print(f"✅ Bot logged in as {bot.user}")
    print(f"🔔 Daily mints will be posted to channel {CHANNEL_ID} at 09:00 UTC")
    
    # Start scheduler if not already running
    global scheduler_thread
    if scheduler_thread is None or not scheduler_thread.is_alive():
        scheduler_thread = threading.Thread(target=schedule_mints, daemon=True)
        scheduler_thread.start()


@bot.command(name="mint")
async def manual_mint(ctx):
    """Manually trigger daily mint posting"""
    await ctx.send("🌿 Fetching today's NFT mints...")
    await post_daily_mints()


@bot.command(name="ping")
async def ping(ctx):
    """Check bot latency"""
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")


if __name__ == "__main__":
    if not DISCORD_TOKEN or not CHANNEL_ID:
        print("❌ Error: DISCORD_TOKEN and CHANNEL_ID must be set in .env file")
        exit(1)
    
    bot.run(DISCORD_TOKEN)
