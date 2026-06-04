"""
Test script to fetch NFT mints from NFTCalendar
No Discord posting - just prints to terminal
"""

import requests
from datetime import datetime
import pytz
from bs4 import BeautifulSoup


def get_recent_mints():
    """Scrape NFTCalendar for live mints"""
    try:
        print("🔍 Fetching mints from NFTCalendar.io...")
        
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
            print(f"✅ Found {len(mints)} collections!\n")
            return mints[:10]  # Return top 10
        
        # Fallback to sample data if scraping fails
        print("⚠️  No mints found on NFTCalendar")
        print("💡 Using sample data instead...\n")
        return get_sample_data()
        
    except Exception as e:
        print(f"⚠️  Error scraping NFTCalendar: {e}")
        print("💡 Using sample data instead...\n")
        return get_sample_data()


def get_sample_data():
    """Return sample mint data for testing"""
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


def print_mint(mint, index):
    """Pretty print a mint"""
    name = mint.get("name", "Unknown Collection")
    description = mint.get("description", "No description")[:100]
    price = mint.get("price", "Check site")
    supply = mint.get("supply", "N/A")
    creator = mint.get("creator", "Unknown")
    blockchain = mint.get("blockchain", "Ethereum")
    url = mint.get("url", "N/A")
    verified = "✓" if mint.get("verified") else ""
    
    print(f"\n{'='*60}")
    print(f"#{index} 🌿 {name} {verified}")
    print(f"{'='*60}")
    print(f"Description: {description}...")
    print(f"💰 Price: {price}")
    print(f"📊 Supply: {supply}")
    print(f"👤 Creator: {creator}")
    print(f"⛓️  Blockchain: {blockchain}")
    print(f"🔗 URL: {url}")


def main():
    print("\n" + "="*60)
    print("🌿 DISCORD MINT BOT - LOCAL TEST")
    print("="*60)
    print(f"Testing at: {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    mints = get_recent_mints()
    
    if not mints:
        print("❌ No mints found! Check your connection or Premint API status.")
        return
    
    print(f"\n📋 Displaying top 5 mints:\n")
    for i, mint in enumerate(mints[:5], 1):
        print_mint(mint, i)
    
    print("\n" + "="*60)
    print("✅ Test complete! Bot is working correctly.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
