#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration module for TeleClean bot.
Contains static configurations and environment variable fallbacks.
"""

import os

# MongoDB Connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

# Bot owner's Telegram ID
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# Message deletion thresholds (in minutes)
USER_MESSAGES = int(os.environ.get("USER_MESSAGES", "60"))  # 1 hour by default
ALL_MESSAGES = int(os.environ.get("ALL_MESSAGES", "1440"))  # 24 hours by default

# List of user IDs whose messages are exempt from deletion
EXCEPTIONS = [int(id_) for id_ in os.environ.get("EXCEPTIONS", "").split(",") if id_]

# If True, will simulate deletions without actually deleting messages
DRY_RUN = os.environ.get("DRY_RUN", "False").lower() == "true"

# Bot token from BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Update interval for live progress updates (in seconds)
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", "5"))

# Log level
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
