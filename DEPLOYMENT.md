# TeleClean Deployment Guide

This guide walks you through deploying the TeleClean bot using GitHub Actions. The bot runs every 15 minutes to clean up messages in Telegram groups and channels based on configurable time thresholds.

## Step 1: Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions to create your bot
3. **Important:** Turn OFF privacy mode with `/setprivacy` command
4. Save the bot token (will look like `1234567890:ABCDefghijklmnopQRSTuvwxyz`)

## Step 2: Set Up a MongoDB Database

1. Create a free MongoDB Atlas account at [mongodb.com](https://www.mongodb.com/)
2. Create a new cluster (free tier works fine)
3. Set up a database user with read/write permissions
4. Get your MongoDB connection URI (looks like `mongodb+srv://username:password@cluster.mongodb.net/`)

## Step 3: Set Up GitHub Repository

1. Fork or clone the TeleClean repository
2. Go to your repository Settings → Secrets and Variables → Actions
3. Add the following secrets:

| Secret | Value |
|--------|-------|
| `BOT_TOKEN` | Your bot token from Step 1 |
| `MONGO_URI` | Your MongoDB URI from Step 2 |
| `OWNER_ID` | Your Telegram user ID (get from [@userinfobot](https://t.me/userinfobot)) |
| `EXCEPTIONS` | Comma-separated list of IDs to exempt from deletion |

## Step 4: Configure Message Deletion Thresholds

Add these optional secrets to customize deletion behavior:

| Secret | Description | Default |
|--------|-------------|---------|
| `USER_MESSAGES` | Minutes to keep user messages | 60 (1 hour) |
| `ALL_MESSAGES` | Minutes to keep all messages | 1440 (24 hours) |
| `DRY_RUN` | Set to "True" to simulate without deleting | False |

## Step 5: Add Bot to Groups/Channels

1. Add your bot to a group or channel 
2. Make the bot an admin with permission to delete messages
3. The bot will automatically detect it's been added

## Step 6: Enable GitHub Actions

1. Go to Actions tab in your repository
2. Enable workflows if they're not already enabled
3. Run the workflow manually once to test

## Troubleshooting

If you encounter issues:

1. Check GitHub Actions logs for errors
2. Ensure your bot is an admin in all groups/channels
3. Verify MongoDB connection string is correct
4. Check that your OWNER_ID is correct

## Customizing Exceptions

See [EXCEPTIONS-GUIDE.md](EXCEPTIONS-GUIDE.md) for detailed instructions on how to configure which users, bots, and channels are exempt from message deletion.

## Running Locally for Testing

```powershell
# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:BOT_TOKEN = "your_bot_token"
$env:MONGO_URI = "your_mongodb_uri"
$env:OWNER_ID = "your_telegram_id"
$env:DRY_RUN = "True"  # Important for testing!

# Run the bot
python main.py
```
