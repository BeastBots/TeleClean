#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Start alert for TeleClean bot.
Sends notification when bot is started.
"""

import html
from typing import Dict, Any
from datetime import datetime
from loguru import logger
from telegram import Bot
from telegram.constants import ParseMode

class StartAlert:
    """Sends alert when bot starts running."""
    
    def __init__(self, bot: Bot, owner_id: int):
        """Initialize the start alert.
        
        Args:
            bot: Telegram Bot instance
            owner_id: Telegram user ID of the bot owner
        """
        self.bot = bot
        self.owner_id = owner_id
    
    async def send_alert(self, config: Dict[str, Any]) -> bool:
        """Send alert that the bot is starting.
        
        Args:
            config: Bot configuration dictionary
            
        Returns:
            bool: True if alert was sent successfully
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format message
            message = (
                f"🟢 <b>TeleClean Bot Started</b>\n\n"
                f"<b>Time:</b> {current_time}\n\n"                f"<b>Configuration:</b>\n"
                f"• User messages: {config['user_messages']} minutes\n"
                f"• All messages: {config['all_messages']} minutes\n"
                f"• Exceptions: {len(config['exceptions'])} (users & channels)\n"
                f"• Dry run: {'Yes' if config['dry_run'] else 'No'}\n\n"
                f"<i>Starting message deletion process...</i>"
            )
            
            # Send message to owner
            await self.bot.send_message(
                chat_id=self.owner_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            logger.info("Start alert sent to owner")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send start alert: {str(e)}")
            return False
