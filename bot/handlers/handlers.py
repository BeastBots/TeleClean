#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Handlers module for TeleClean bot.
Imports and registers all handler modules.
"""

import asyncio
from typing import Dict, Any
from loguru import logger
from telegram.ext import Application

from config import OWNER_ID
from bot.handlers.error import ErrorHandler
from bot.handlers.chat_handler import ChatHandler
from bot.handlers.config_handler import ConfigHandler


async def setup_handlers(application: Application) -> None:
    """Set up all handlers for the bot.
    
    Args:
        application: Telegram Application instance
    """
    logger.info("Setting up handlers")
    
    # Load the configuration
    config_handler = ConfigHandler()
    application.bot_data["config"] = config_handler.to_dict()
    
    # Initialize error handler
    error_handler = ErrorHandler(OWNER_ID)
    error_handler.register_handlers(application)
    application.bot_data["error_handler"] = error_handler
    
    # Initialize chat handler
    chat_handler = ChatHandler(application)
    application.bot_data["chat_handler"] = chat_handler
    
    logger.info("All handlers set up successfully")
