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

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Premint API endpoints
PREMINT_API_BASE = "https://api.premint.xyz"

# Global variables
scheduler_thread = None


def get_recent_mints():
    """Fetch today's active NFT mints from Premint"""
    try:
        from datetime import datetime, timedelta
        
        # Get mints for today
        url = f"{PREMINT_API_BASE}/collections/upcoming"
        params = {
            "limit": 10,
            "sort": "minting_soon",
            "status": "minting_now"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            mints = data.get("data", [])
            # Filter for today's mints
            today = datetime.now().date()
            today_mints = []
            for mint in mints:
                try:
                    mint_date = mint.get("mint_date", "")
                    if mint_date:
                        mint_datetime = datetime.fromisoformat(mint_date.replace('Z', '+00:00')).date()
                        if mint_datetime == today:
                            today_mints.append(mint)
                except:
                    pass
            return today_mints if today_mints else mints[:5]
        else:
            print(f"Error fetching from Premint: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching mints: {e}")
        return []


def format_mint_embed(mint):
    """Format Premint mint data as Discord embed"""
    try:
        name = mint.get("name", "Unknown Collection")
        description = mint.get("description", "No description available")[:250]
        
        embed = discord.Embed(
            title=name,
            description=description,
            color=discord.Color.gold(),
            timestamp=datetime.now(pytz.UTC)
        )
        
        # Add mint image
        image_url = mint.get("image_url") or mint.get("logo")
        if image_url:
            embed.set_thumbnail(url=image_url)
        
        # Mint price
        price = mint.get("price", {})
        if isinstance(price, dict):
            price_str = price.get("value", "Check site")
        else:
            price_str = str(price) if price else "Check site"
        
        embed.add_field(
            name="💰 Price",
            value=price_str,
            inline=True
        )
        
        # Mint supply
        supply = mint.get("supply", "N/A")
        embed.add_field(
            name="📊 Supply",
            value=str(supply),
            inline=True
        )
        
        # Mint time
        mint_date = mint.get("mint_date", "TBA")
        embed.add_field(
            name="🕐 Mint Time",
            value=mint_date[:16] if mint_date else "TBA",
            inline=True
        )
        
        # Creator/Project
        creator = mint.get("creator_name") or mint.get("creator", "Unknown")
        embed.add_field(
            name="👤 Creator",
            value=creator,
            inline=True
        )
        
        # Blockchain
        blockchain = mint.get("blockchain", "Ethereum")
        embed.add_field(
            name="⛓️ Chain",
            value=blockchain,
            inline=True
        )
        
        # Links
        premint_url = mint.get("url") or f"https://www.premint.xyz/{mint.get('slug', '')}"
        embed.add_field(
            name="🔗 Links",
            value=f"[Premint]({premint_url})",
            inline=False
        )
        
        embed.set_footer(text="🌿 Daily Mint Bot • Powered by Premint")
        
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
        
        # Send header
        embed = discord.Embed(
            title="🌿 Today's NFT Mints",
            description=f"Hot collections minting now ({len(mints)} found)",
            color=discord.Color.gold(),
            timestamp=datetime.now(pytz.UTC)
        )
        embed.set_footer(text="Data from Premint • Use !mint to refresh")
        
        await channel.send(embed=embed)
        
        # Post top mints
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
