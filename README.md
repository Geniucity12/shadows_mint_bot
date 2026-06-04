# Discord Daily Mint Bot 🌿

A Discord bot that automatically fetches and posts daily NFT mints from OpenSea to your Discord server.

## Features

- ✅ Automatic daily minting posts at 9:00 AM UTC
- ✅ Fetches data from OpenSea API
- ✅ Beautiful Discord embeds with collection info
- ✅ Manual trigger with `!mint` command
- ✅ Status check with `!ping` command

## Prerequisites

- Python 3.8+
- Discord Bot Token
- OpenSea API Key
- Discord Channel ID

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name your bot and click "Create"
4. Go to "Bot" section and click "Add Bot"
5. Under "TOKEN", click "Copy" to copy your token
6. Go to "OAuth2" → "URL Generator"
   - Select `bot` scope
   - Select permissions: `Send Messages`, `Read Messages/View Channels`, `Embed Links`
7. Copy the generated URL and open it to invite the bot to your server

### 3. Get Your Channel ID

1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click the channel where you want mints posted
3. Click "Copy Channel ID"

### 4. Get OpenSea API Key

1. Go to [OpenSea Docs](https://docs.opensea.io/)
2. Sign up for API access
3. Copy your API key

### 5. Configure Environment Variables

Edit `.env` and add:
```
DISCORD_TOKEN=your_bot_token_here
CHANNEL_ID=your_channel_id_here
OPENSEA_API_KEY=your_opensea_api_key_here
```

### 6. Run the Bot

```bash
python bot.py
```

You should see:
```
✅ Bot logged in as YourBotName
🔔 Daily mints will be posted to channel XXXXX at 09:00 UTC
```

## Commands

- `!ping` - Check bot latency
- `!mint` - Manually post today's NFT mints

## How It Works

1. The bot connects to Discord and waits for 9:00 AM UTC
2. At the scheduled time, it fetches recent NFT collections from OpenSea
3. It formats the data into attractive Discord embeds
4. Posts the top 5 new mints to your designated channel

## Troubleshooting

**Bot not posting?**
- Verify bot has "Send Messages" and "Embed Links" permissions in the channel
- Check that CHANNEL_ID is correct
- Ensure OPENSEA_API_KEY is valid

**API errors?**
- Check OpenSea API status
- Verify your API key hasn't been revoked
- Rate limits may apply; consider upgrading your OpenSea plan

**Bot not starting?**
- Verify all environment variables are set in `.env`
- Check Python version is 3.8+
- Ensure all dependencies installed: `pip install -r requirements.txt`

## Deployment

For continuous operation, consider hosting on:
- Heroku (free tier available)
- AWS Lambda
- DigitalOcean
- Your own VPS

## License

MIT

## Support

If you encounter issues, check the bot logs for error messages and verify all configuration steps.
