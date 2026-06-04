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
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Global variables
scheduler_thread = None
last_posted_mints = []  # Track posted mints for skip functionality


def get_recent_mints():
    """Scrape NFTCalendar for live mints"""
    try:
        # Scrape NFTCalendar live mints
        url = "https://nftcalendar.io/mints/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        mints = []
        # Find all mint event cards
        cards = soup.find_all('a', {'class': lambda x: x and 'event' in x.lower()})
        
        for card in cards[:15]:  # Get up to 15 mints
            try:
                # Extract collection name and link
                title_elem = card.find('h2') or card.find('h3')
                if not title_elem:
                    title_elem = card
                
                title = title_elem.get_text(strip=True) if title_elem else "Unknown"
                link = card.get('href', 'https://nftcalendar.io')
                if not link.startswith('http'):
                    link = 'https://nftcalendar.io' + link
                
                # Extract description/status from card text
                description = card.get_text(strip=True)[:200]
                
                # Check for verified badge
                verified = 'verified' in card.get_text(strip=True).lower()
                
                if title and title != "Unknown":
                    mints.append({
                        "name": title,
                        "description": description[:100] if description else "NFT Collection Minting",
                        "price": "Check site",
                        "supply": "N/A",
                        "creator": "Verified" if verified else "Community",
                        "blockchain": "Multi-chain",
                        "url": link,
                        "verified": verified
                    })
            except Exception as e:
                print(f"Error parsing card: {e}")
                continue
        
        if mints:
            return mints[:10]  # Return top 10
        
        # Fallback to sample data if scraping fails
        return get_sample_mints()
        
    except Exception as e:
        print(f"⚠️  Error scraping NFTCalendar: {e}")
        print(f"💡 Using sample data instead...")
        return get_sample_mints()


def get_sample_mints():
    """Return sample mint data for demo purposes"""
    return [
        {
            "name": "The Griftettes",
            "description": "Feminine cast conjured from the network by XCOPY",
            "price": "Check site",
            "supply": "Limited",
            "creator": "Verified",
            "blockchain": "Ethereum",
            "url": "https://nftcalendar.io/event/thegriftettes-nft/",
            "verified": True
        },
        {
            "name": "FMP 02",
            "description": "Digital art collection on NFTCalendar",
            "price": "Check site",
            "supply": "Limited",
            "creator": "Verified",
            "blockchain": "Ethereum",
            "url": "https://nftcalendar.io/event/fmp02-nft/",
            "verified": True
        },
        {
            "name": "Green Lights",
            "description": "The dream - Limited edition collection",
            "price": "Check site",
            "supply": "Limited",
            "creator": "Verified",
            "blockchain": "Ethereum",
            "url": "https://nftcalendar.io/event/green-lights26/",
            "verified": True
        }
    ]


def format_mint_embed(mint):
    """Format mint data as Discord embed"""
    try:
        name = mint.get("name", "Unknown Collection")
        description = mint.get("description", "Check the collection")[:250]
        
        embed = discord.Embed(
            title=name,
            description=description,
            color=discord.Color.gold(),
            timestamp=datetime.now(pytz.UTC)
        )
        
        # Add price
        price = mint.get("price", "Check site")
        embed.add_field(
            name="💰 Price",
            value=str(price),
            inline=True
        )
        
        # Supply
        supply = mint.get("supply", "N/A")
        embed.add_field(
            name="📊 Supply",
            value=str(supply),
            inline=True
        )
        
        # Creator
        creator = mint.get("creator", "Unknown")
        embed.add_field(
            name="👤 Creator",
            value=creator,
            inline=True
        )
        
        # Blockchain
        blockchain = mint.get("blockchain", "Ethereum")
        embed.add_field(
            name="⛓️  Blockchain",
            value=blockchain,
            inline=True
        )
        
        # Link
        url = mint.get("url", "#")
        embed.add_field(
            name="🔗 Visit",
            value=f"[Open Collection]({url})",
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
                description="No mints found right now. Check back later!",
                color=discord.Color.greyple(),
                timestamp=datetime.now(pytz.UTC)
            )
            await channel.send(embed=embed)
            return
        
        # Send header
        embed = discord.Embed(
            title="🌿 Today's Top Mints",
            description=f"Hottest NFT collections minting now ({len(mints)} found)",
            color=discord.Color.gold(),
            timestamp=datetime.now(pytz.UTC)
        )
        embed.set_footer(text="Data from NFT aggregators • Use !mint to refresh")
        
        await channel.send(embed=embed)
        
        # Post top mints
        for mint in mints[:5]:
            mint_embed = format_mint_embed(mint)
            if mint_embed:
                await channel.send(embed=mint_embed)
                time.sleep(0.5)
        
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


@bot.command(name="skip")
async def skip_last_mint(ctx):
    """Remove last posted mint from the channel"""
    try:
        # Get the last message in the channel
        async for message in ctx.channel.history(limit=5):
            if message.author == bot.user and message.embeds:
                # Found a bot embed, delete it
                await message.delete()
                await ctx.send("✅ Mint removed!")
                return
        await ctx.send("❌ No recent mints to skip.")
    except Exception as e:
        await ctx.send(f"❌ Error removing mint: {e}")


@bot.command(name="ping")
async def ping(ctx):
    """Check bot latency"""
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")


if __name__ == "__main__":
    if not DISCORD_TOKEN or not CHANNEL_ID:
        print("❌ Error: DISCORD_TOKEN and CHANNEL_ID must be set in .env file")
        exit(1)
    
    bot.run(DISCORD_TOKEN)
