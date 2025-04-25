#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Stop alert for TeleClean bot.
Sends notification when bot has finished processing.
"""

import html
from typing import Dict, Any
from datetime import datetime, timedelta
from loguru import logger
from telegram import Bot
from telegram.constants import ParseMode

class StopAlert:
    """Sends alert when bot finishes running."""
    
    def __init__(self, bot: Bot, owner_id: int):
        """Initialize the stop alert.
        
        Args:
            bot: Telegram Bot instance
            owner_id: Telegram user ID of the bot owner
        """
        self.bot = bot
        self.owner_id = owner_id
    
    async def send_alert(self, stats: Dict[str, int], 
                        execution_time: float) -> bool:
        """Send alert that the bot has finished running.
        
        Args:
            stats: Dictionary with deletion statistics
            execution_time: Total execution time in seconds
            
        Returns:
            bool: True if alert was sent successfully
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format execution time
            exec_time_str = self._format_execution_time(execution_time)
            
            # Calculate success rate
            success_rate = 0
            if stats['total_messages'] > 0:
                success_rate = (stats['deleted_messages'] / stats['total_messages']) * 100
            
            # Format message
            message = (
                f"🔴 <b>TeleClean Bot Finished</b>\n\n"
                f"<b>Time:</b> {current_time}\n"
                f"<b>Execution Time:</b> {exec_time_str}\n\n"
                f"<b>Final Statistics:</b>\n"
                f"• Chats Processed: {stats['chats_processed']}\n"
                f"• Total Messages: {stats['total_messages']}\n"
                f"• Deleted: {stats['deleted_messages']}\n"
                f"• Skipped: {stats['skipped_messages']}\n"
                f"• Exempt: {stats['exempt_messages']}\n"
                f"• Errors: {stats['error_messages']}\n"
                f"• Success Rate: {success_rate:.1f}%\n\n"
                f"<i>Bot will run again in the next scheduled cycle.</i>"
            )
            
            # Send message to owner
            await self.bot.send_message(
                chat_id=self.owner_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            logger.info("Stop alert sent to owner")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send stop alert: {str(e)}")
            return False
    
    def _format_execution_time(self, seconds: float) -> str:
        """Format execution time into a readable string.
        
        Args:
            seconds: Execution time in seconds
            
        Returns:
            str: Formatted time string
        """
        time_delta = timedelta(seconds=seconds)
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")
            
        return " ".join(parts)
