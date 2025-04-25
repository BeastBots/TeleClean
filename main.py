#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry script for TeleClean bot.
"""

import asyncio
import time
from loguru import logger
import sys

from config import BOT_TOKEN, MONGO_URI, OWNER_ID, EXCEPTIONS
from bot.database.database import Database
from bot.handlers.config_handler import ConfigHandler
from bot.handlers.executor import Executor
from bot.database.analyzer import DatabaseAnalyzer
from bot.alerts.start import StartAlert
from bot.alerts.stop import StopAlert
from bot.alerts.error import ErrorAlert
from telegram.ext import ApplicationBuilder


async def run_cleaner():
    """Main deletion process function."""
    start_time = time.time()
    
    try:
        # Configure logger
        logger.remove()
        logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
        logger.add("logs/teleclean_{time}.log", rotation="1 day", retention="7 days")
        
        logger.info("Starting TeleClean bot")
        
        # Load configuration
        config_handler = ConfigHandler()
        config = config_handler.to_dict()
        
        # Initialize bot
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        await application.initialize()
        bot = application.bot
        
        # Initialize database
        db = Database(MONGO_URI)
        await db.setup_collections()
        
        # Send start alert
        start_alert = StartAlert(bot, OWNER_ID)
        await start_alert.send_alert(config)
        
        # Run database analyzer
        analyzer = DatabaseAnalyzer(application, db)
        valid_chats, removed_chats = await analyzer.verify_chat_records()
        logger.info(f"Database analysis: {valid_chats} valid chats, {removed_chats} removed")
        
        # Run executor for message deletion
        executor = Executor(bot, db, config)
        stats = await executor.process_all_chats()
        
        # Send completion alert
        execution_time = time.time() - start_time
        stop_alert = StopAlert(bot, OWNER_ID)
        await stop_alert.send_alert(stats, execution_time)
        
        # Close database connection
        await db.close()
        
        # Shutdown bot application
        await application.shutdown()
        
        logger.info(f"TeleClean completed in {execution_time:.2f} seconds")
        return 0
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        
        try:
            # Send error alert
            application = ApplicationBuilder().token(BOT_TOKEN).build()
            await application.initialize()
            bot = application.bot
            
            error_alert = ErrorAlert(bot, OWNER_ID)
            await error_alert.send_alert(e, "Main process error")
            
            await application.shutdown()
        except Exception as alert_error:
            logger.error(f"Failed to send error alert: {str(alert_error)}")
            
        return 1


def main():
    """Script entry point."""
    try:
        exit_code = asyncio.run(run_cleaner())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
