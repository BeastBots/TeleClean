# TG Auto Deletion Bot

An automated Telegram bot that deletes messages from groups after specified timeouts to help avoid copyright issues.

## Features

- Deletes user messages after a configurable timeout (default: 15 minutes)
- Deletes bot messages after a configurable timeout
- Runs automatically via GitHub Actions
- Configurable exceptions for specific users or channels

## Setup

1. Fork this repository
2. Set up your Telegram API credentials in the repository secrets
3. Configure the timeouts in `config.env`
4. Enable GitHub Actions

## Configuration

Edit the `config.env` file to set up your bot:

- `OWNER_ID`: Your Telegram user ID
- `TELEGRAM_API`: Your Telegram API ID
- `TELEGRAM_HASH`: Your Telegram API Hash
- `BOT_TOKEN`: Your bot token from @BotFather
- `USER_TIMEOUT`: Time in seconds before deleting user messages
- `BOT_TIMEOUT`: Time in hours before deleting bot messages
- `EXCEPTIONS`: Comma-separated list of user/channel IDs to exempt from deletion

## License

MIT 