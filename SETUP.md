# TG Auto Deletion Bot Setup Guide

## Prerequisites

1. Python 3.7 or higher
2. Telegram API credentials (API ID and API Hash)
3. Telegram Bot Token from @BotFather
4. GitHub account (for GitHub Actions deployment)

## Local Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/tg-auto-deletion-bot.git
   cd tg-auto-deletion-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the `config.env` file:
   ```
   # Telegram API Credentials
   OWNER_ID=your_telegram_id
   TELEGRAM_API=your_api_id
   TELEGRAM_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   
   # Deletion Timeouts
   USER_TIMEOUT=900  # 15 minutes in seconds (default)
   BOT_TIMEOUT=24    # 24 hours (default)
   
   # Exceptions (comma-separated IDs to exclude from deletion)
   EXCEPTIONS=channel_id1,user_id1
   ```

4. Run the bot:
   ```
   python startup.py
   ```

## GitHub Actions Setup

1. Fork this repository on GitHub.

2. Add your configuration as GitHub Secrets:
   - Go to your forked repository on GitHub
   - Navigate to Settings > Secrets > Actions
   - Add the following secrets:
     - `OWNER_ID`: Your Telegram ID
     - `TELEGRAM_API`: Your Telegram API ID
     - `TELEGRAM_HASH`: Your Telegram API Hash
     - `BOT_TOKEN`: Your Bot Token
     - `USER_TIMEOUT` (optional): Custom user message timeout in seconds
     - `BOT_TIMEOUT` (optional): Custom bot message timeout in hours
     - `EXCEPTIONS` (optional): Comma-separated list of IDs to exclude from deletion

3. Enable GitHub Actions:
   - Go to the "Actions" tab in your repository
   - Click "I understand my workflows, go ahead and enable them"

4. Trigger the workflow:
   - The bot will automatically run every 15 minutes
   - You can also manually trigger it by going to Actions > Run TG Auto Deletion Bot > Run workflow

## Bot Commands

- `/start` - Start the bot
- `/status` - Check bot status (queued messages, timeouts)
- `/settimeout [user|bot] [time]` - Set deletion timeout
- `/clear [user|bot|all]` - Clear message queue
- `/help` - Show help information

## Getting Your Telegram API Credentials

1. Visit https://my.telegram.org/auth
2. Log in with your phone number
3. Click on "API Development Tools"
4. Fill in the required fields (App title, Short name)
5. You'll receive your API ID and API Hash

## Getting Your Bot Token

1. Open Telegram and search for @BotFather
2. Start a chat and send /newbot
3. Follow the instructions to create a new bot
4. You'll receive a bot token that looks like `123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ`

## How to Get Telegram IDs

- For your own ID: Send a message to @userinfobot
- For a channel ID: Forward a message from the channel to @userinfobot 