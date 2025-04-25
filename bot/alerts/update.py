#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Update alert for TeleClean bot.
Sends live updates during deletion process.
"""

import html
from typing import Dict, Any
from datetime import datetime
from loguru import logger
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError


class UpdateAlert:
    """Sends live progress updates during deletion process."""
    
    def __init__(self, bot: Bot, owner_id: int):
        """Initialize the update alert.
        
        Args:
            bot: Telegram Bot instance
            owner_id: Telegram user ID of the bot owner
        """
        self.bot = bot
        self.owner_id = owner_id
        self.message_id = None
    
    async def send_update(self, completed: int, total: int, stats: Dict[str, int],
                         in_progress: bool = True) -> bool:
        """Send or update progress information.
        
        Args:
            completed: Number of chats processed
            total: Total number of chats to process
            stats: Dictionary with deletion statistics
            in_progress: Whether the deletion is still in progress
            
        Returns:
            bool: True if update was sent successfully
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Calculate progress percentage
            progress_pct = (completed / total) * 100 if total > 0 else 0
            
            # Create progress bar
            progress_bar = self._create_progress_bar(progress_pct)
            
            # Status emoji
            status_emoji = "⏳" if in_progress else "✅"
            
            # Format message
            message = (
                f"{status_emoji} <b>TeleClean Progress Update</b>\n\n"
                f"<b>Time:</b> {current_time}\n\n"
                f"<b>Progress:</b> {completed}/{total} chats ({progress_pct:.1f}%)\n"
                f"{progress_bar}\n\n"
                f"<b>Statistics:</b>\n"
                f"• Total messages: {stats['total_messages']}\n"
                f"• Deleted: {stats['deleted_messages']}\n"
                f"• Skipped: {stats['skipped_messages']}\n"
                f"• Exempt: {stats['exempt_messages']}\n"
                f"• Errors: {stats['error_messages']}\n"
            )
            
            # Add in-progress or completion message
            if in_progress:
                message += "\n<i>Deletion in progress...</i>"
            else:
                message += "\n<i>Deletion process complete!</i>"
            
            # Send or edit message
            if not self.message_id:
                # First update - send new message
                sent_msg = await self.bot.send_message(
                    chat_id=self.owner_id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
                self.message_id = sent_msg.message_id
            else:
                # Subsequent updates - edit existing message
                await self.bot.edit_message_text(
                    text=message,
                    chat_id=self.owner_id,
                    message_id=self.message_id,
                    parse_mode=ParseMode.HTML
                )
            
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send update alert: {str(e)}")
            # If editing failed, try sending a new message
            if self.message_id:
                try:
                    sent_msg = await self.bot.send_message(
                        chat_id=self.owner_id,
                        text=message,
                        parse_mode=ParseMode.HTML
                    )
                    self.message_id = sent_msg.message_id
                    return True
                except Exception as nested_e:
                    logger.error(f"Failed to send new update message: {str(nested_e)}")
            return False
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a text-based progress bar.
        
        Args:
            percentage: Progress percentage (0-100)
            width: Width of the progress bar in characters
            
        Returns:
            str: The progress bar as a string
        """
        filled = int(width * percentage / 100)
        return f"[{'█' * filled}{' ' * (width - filled)}]"
