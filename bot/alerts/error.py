#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Error alert for TeleClean bot.
Sends notification when bot encounters an error.
"""

import html
import traceback
from typing import Optional
from datetime import datetime
from loguru import logger
from telegram import Bot, Message
from telegram.constants import ParseMode
from telegram.error import TelegramError

class ErrorAlert:
    """Sends alert when bot encounters an error."""
    
    def __init__(self, bot: Bot, owner_id: int):
        """Initialize the error alert.
        
        Args:
            bot: Telegram Bot instance
            owner_id: Telegram user ID of the bot owner
        """
        self.bot = bot
        self.owner_id = owner_id
    
    async def send_alert(self, error: Exception, 
                        context: Optional[str] = None) -> bool:
        """Send alert about an error.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            bool: True if alert was sent successfully
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get traceback
            tb_string = "".join(traceback.format_exception(
                None, error, error.__traceback__
            ))
            
            # Format error message
            message = (
                f"⚠️ <b>TeleClean Error Occurred</b>\n\n"
                f"<b>Time:</b> {current_time}\n"
                f"<b>Error Type:</b> {type(error).__name__}\n"
                f"<b>Error Message:</b> {html.escape(str(error))}\n"
            )
            
            # Add context if provided
            if context:
                message += f"\n<b>Context:</b> {html.escape(context)}\n"
                
            # Send message to owner
            msg = await self.bot.send_message(
                chat_id=self.owner_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            # Send traceback as a separate quoted message
            traceback_msg = (
                f"<pre>{html.escape(tb_string)}</pre>"
            )
            
            # Truncate if too long
            if len(traceback_msg) > 4000:
                traceback_msg = traceback_msg[:4000] + "...</pre>"
                
            await self.bot.send_message(
                chat_id=self.owner_id,
                text=traceback_msg,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=msg.message_id
            )
            
            logger.info("Error alert sent to owner")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send error alert: {str(e)}")
            
            # Fallback to simpler message if HTML formatting fails
            try:
                await self.bot.send_message(
                    chat_id=self.owner_id,
                    text=f"ERROR: {str(error)}\n\nAdditional error sending formatted alert: {str(e)}"
                )
                return True
            except:
                return False
                
    async def send_rate_limit_alert(self) -> bool:
        """Send alert about rate limiting.
        
        Returns:
            bool: True if alert was sent successfully
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format message
            message = (
                f"⚠️ <b>TeleClean Rate Limit Warning</b>\n\n"
                f"<b>Time:</b> {current_time}\n\n"
                f"The bot is experiencing rate limits from Telegram API.\n"
                f"Deletion operations will slow down to avoid further rate limiting.\n\n"
                f"<i>This is normal during heavy deletion operations.</i>"
            )
            
            # Send message to owner
            await self.bot.send_message(
                chat_id=self.owner_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            logger.info("Rate limit alert sent to owner")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send rate limit alert: {str(e)}")
            return False
