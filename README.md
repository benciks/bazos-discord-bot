# Golf 5 Parts Bazos Bot

Discord bot that monitors bazos.sk for VW Golf 5 spare parts and sends notifications when new listings appear. Detects reposted ads by content matching.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```
DISCORD_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=your_channel_id
```

## Run

```bash
source venv/bin/activate
python -m src.main
```

## Bot Commands

- `!status` - show stats
- `!check` - force immediate check

## Config

Edit `SEARCH_QUERIES` in `.env` to customize searches (comma-separated).

Default: `golf 5 diely,golf 5 nd,golf 5 blatnik,golf 5 naraznik,golf 5 svetlo,golf 5 la7w`
