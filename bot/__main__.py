#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main module for TeleClean bot.
"""

import asyncio
from loguru import logger
import telegram
from telegram.ext import ApplicationBuilder

from config import BOT_TOKEN, MONGO_URI
from bot.database.database import Database
from bot.handlers.handlers import setup_handlers


async def main():
    """Main entry point for the bot."""
    # Configure logger
    logger.info("Starting TeleClean bot")
    
    # Initialize the bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Initialize database
    db = Database(MONGO_URI)
    await db.setup_collections()
    
    # Add db to application context
    application.bot_data["db"] = db
    
    # Setup handlers
    await setup_handlers(application)
    
    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Run until disconnected
    await application.updater.stop()
    await application.stop()
    await application.shutdown()
    
    # Close database connection
    await db.close()
    

if __name__ == "__main__":
    asyncio.run(main())
