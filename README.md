# TeleClean Bot

A professional-grade Telegram bot that automatically deletes messages in groups and channels based on time thresholds. Built with modern Python and running on GitHub Actions.

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/username/teleclean/teleclean.yml?style=flat-square)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)
![License](https://img.shields.io/github/license/username/teleclean?style=flat-square)

## 📖 Overview

TeleClean is a Telegram bot that automatically cleans up messages in groups and channels based on configurable time thresholds. It runs independently on GitHub Actions every 15 minutes, providing an effortless way to maintain clean conversation spaces.

### Features

- **Fully automated** - Runs entirely via GitHub Actions
- **Customizable thresholds** - Set different deletion times for:
  - Regular user messages
  - All messages (including bot messages)
- **Exempt users** - Configure specific users whose messages won't be deleted
- **Detailed alerts** - Receive notifications about:
  - Bot startup
  - Live deletion progress
  - Completion statistics
  - Detailed error reports
- **Dry run mode** - Test deletion rules without actually removing messages
- **MongoDB integration** - Reliable storage of chat data and deletion history

## 🛠️ Setup

### Prerequisites

- Python 3.10 or higher
- MongoDB database (cloud or self-hosted)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- GitHub account (for running GitHub Actions)

### Configuration

1. **Bot Creation**
   - Create a new bot with [@BotFather](https://t.me/BotFather)
   - Turn OFF privacy mode (important for group message access)
   - Copy your bot token

2. **MongoDB Setup**
   - Create a MongoDB database (free tier on MongoDB Atlas works fine)
   - Get your MongoDB URI connection string

3. **GitHub Repository**
   - Fork or clone this repository
   - Set up the following GitHub Secrets:

     | Secret | Description | Default |
     |--------|-------------|---------|
     | `BOT_TOKEN` | Telegram Bot Token | (required) |
     | `MONGO_URI` | MongoDB Connection URI | (required) |
     | `OWNER_ID` | Your Telegram User ID | (required) |
     | `USER_MESSAGES` | Minutes to keep user messages | 60 (1 hour) |
     | `ALL_MESSAGES` | Minutes to keep all messages | 1440 (24 hours) |
     | `EXCEPTIONS` | Comma-separated list of exempt user and channel IDs | (empty) |
     | `DRY_RUN` | "True" to simulate deletions without deleting | False |
     | `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | INFO |

## 🚀 Usage

### Adding the Bot to Groups/Channels

1. Add your bot to a group or channel
2. Make the bot an admin with at minimum the "Delete Messages" permission
3. The bot will automatically detect it's been added and start tracking the chat
4. Messages will be deleted based on your configured thresholds during each run

### Configuring Exceptions

You can exempt specific users and channels from message deletion:

1. **User Exceptions**: Add user IDs as positive integers
2. **Channel Exceptions**: Add channel IDs as negative integers (usually starting with -100)

Example format for the `EXCEPTIONS` setting:

```text
12345,-1001234567890,98765
```

This would exempt:

- User with ID 12345
- Channel with ID -1001234567890
- User with ID 98765

To get channel IDs, you can:

1. Forward a message from the channel to @userinfobot
2. Use @username_to_id_bot to convert channel usernames to IDs

### Bot Commands

- `/start` - Initialize the bot (in private chat) or verify it's active (in groups)

### Running Locally (Development/Testing)

To run the bot locally:

1. Clone the repository
2. Install dependencies: 
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   export BOT_TOKEN="your_bot_token"
   export MONGO_URI="your_mongodb_uri"
   export OWNER_ID="your_telegram_id"
   export DRY_RUN="True"  # For testing without deleting
   ```
4. Run the bot: `python main.py`

## 🧠 Technical Details

### Project Structure

```
TeleClean/
├── main.py                # Entry script
├── start.py               # GitHub Actions entrypoint script
├── config.py              # Static & env-based config variables
├── requirements.txt
├── README.md

├── bot/
│   ├── __init__.py
│   ├── __main__.py

│   ├── handlers/
│   │   ├── config_handler.py   # Load configs from ENV if missing
│   │   ├── chat_handler.py     # Track which chats/channels the bot is in
│   │   ├── executor.py         # Core deletion logic
│   │   ├── error.py            # Custom error handler
│   │   └── handlers.py         # Import & run all handler modules

│   ├── alerts/
│   │   ├── start.py            # Alert on startup
│   │   ├── update.py           # Live update alerts every 5s
│   │   ├── stop.py             # Alert on successful stop
│   │   └── error.py            # Alert with full traceback on failure

│   ├── database/
│   │   ├── database.py         # MongoDB interface, create db/collections
│   │   ├── analyzer.py         # Scan & clean invalid chat records

├── .github/
│   └── workflows/
│       └── teleclean.yml       # Run every 15 minutes
```

### Database Structure

The bot uses MongoDB with the following collections:

- **records.botpm**: Private chat users
- **records.chats**: Groups the bot is in
- **records.channels**: Channels the bot is in
- **history.interaction**: Log of bot additions/removals
- **history.deletion**: Log of message deletions

### GitHub Actions

The bot runs automatically every 15 minutes via GitHub Actions. The workflow:

1. Sets up Python 3.10
2. Installs dependencies
3. Loads secrets as environment variables
4. Runs the bot via `start.py`
5. Uploads logs as artifacts

## ⚡ Development

### Adding New Features

The modular design makes it easy to extend:

1. Add new handlers in `bot/handlers/`
2. Add new alert types in `bot/alerts/`
3. Extend database functionality in `bot/database/`

### Error Handling

The bot includes comprehensive error handling:

- Catches and reports all exceptions with full tracebacks
- Handles Telegram API errors gracefully
- Automatically notifies the owner of critical issues

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This bot deletes messages. Always test with `DRY_RUN=True` before using in important groups.

---

Made with ❤️ by [Your Name]
