#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Executor module for TeleClean bot.
Core deletion logic for cleaning messages based on time thresholds.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from loguru import logger
from telegram import Bot, Chat
from telegram.error import (
    BadRequest, Forbidden, NetworkError, TimedOut, TelegramError
)

from bot.database.database import Database
from bot.alerts.update import UpdateAlert


class Executor:
    """Handles message deletion based on configured thresholds."""
    
    def __init__(self, bot: Bot, db: Database, config: Dict[str, Any]):
        """Initialize the executor.
        
        Args:
            bot: Telegram Bot instance
            db: Database instance
            config: Configuration dictionary
        """
        self.bot = bot
        self.db = db
        self.config = config
          # Extract config values
        self.user_messages_threshold = config.get("user_messages", 60)  # minutes
        self.all_messages_threshold = config.get("all_messages", 1440)  # minutes
        
        # Get exceptions - can include both user IDs (positive ints) and channel IDs (negative ints)
        # User IDs are typically positive integers
        # Channel IDs are typically negative integers, often starting with -100
        self.exceptions = set(config.get("exceptions", []))
        logger.info(f"Loaded {len(self.exceptions)} exceptions (users and channels)")
        
        self.dry_run = config.get("dry_run", False)
        self.owner_id = config.get("owner_id", 0)
        self.update_interval = config.get("update_interval", 5)  # seconds
        
        # Initialize update alert for live progress reporting
        self.update_alert = UpdateAlert(bot, self.owner_id)
        
        # Stats tracking
        self.stats = {
            "total_messages": 0,
            "deleted_messages": 0,
            "skipped_messages": 0,
            "error_messages": 0,
            "exempt_messages": 0,
            "chats_processed": 0
        }
        
        logger.info("Executor initialized with "
                   f"user_threshold={self.user_messages_threshold}m, "
                   f"all_threshold={self.all_messages_threshold}m, "
                   f"dry_run={self.dry_run}")
    
    async def process_all_chats(self) -> Dict[str, int]:
        """Process all chats and delete messages based on thresholds.
        
        Returns:
            dict: Statistics about the deletion process
        """
        # Reset statistics
        self.stats = {
            "total_messages": 0,
            "deleted_messages": 0,
            "skipped_messages": 0,
            "error_messages": 0,
            "exempt_messages": 0,
            "chats_processed": 0
        }
        
        # Get all active chats
        active_chats = await self.db.get_all_active_chats()
        
        if not active_chats:
            logger.info("No active chats found")
            return self.stats
        
        logger.info(f"Starting deletion process for {len(active_chats)} chats")
        
        # Send initial progress update
        await self.update_alert.send_update(
            0, len(active_chats), self.stats, in_progress=True
        )
        
        # Start tracking time for progress updates
        last_update_time = time.time()
        
        # Process each chat
        for index, chat_data in enumerate(active_chats):
            chat_id = chat_data["_id"]
            chat_type = chat_data.get("type", "group")
            
            try:
                # Process the chat
                logger.info(f"Processing chat {chat_id} ({chat_type})")
                chat_stats = await self.process_chat(chat_id)
                
                # Update overall statistics
                for key, value in chat_stats.items():
                    if key in self.stats:
                        self.stats[key] += value
                
                self.stats["chats_processed"] += 1
                
                # Send progress update if enough time has passed
                current_time = time.time()
                if current_time - last_update_time >= self.update_interval:
                    await self.update_alert.send_update(
                        index + 1, len(active_chats), self.stats, in_progress=True
                    )
                    last_update_time = current_time
                    
            except Exception as e:
                logger.error(f"Error processing chat {chat_id}: {str(e)}")
                continue
        
        # Send final update
        await self.update_alert.send_update(
            len(active_chats), len(active_chats), self.stats, in_progress=False
        )
        
        logger.info(f"Deletion process complete: "
                   f"{self.stats['deleted_messages']} messages deleted, "
                   f"{self.stats['skipped_messages']} skipped, "
                   f"{self.stats['error_messages']} errors")
        
        return self.stats
    
    async def process_chat(self, chat_id: int) -> Dict[str, int]:
        """Process a single chat and delete messages based on thresholds.
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            dict: Statistics about the deletion process for this chat
        """
        chat_stats = {
            "total_messages": 0,
            "deleted_messages": 0,
            "skipped_messages": 0,
            "error_messages": 0,
            "exempt_messages": 0
        }
        
        try:
            # Get chat info to check if bot is still a member and has permissions
            chat = await self.bot.get_chat(chat_id)
            
            # For groups and channels, verify bot has permission to delete messages
            if chat.type in ["group", "supergroup", "channel"]:
                bot_member = await chat.get_member(self.bot.id)
                
                if not bot_member.can_delete_messages:
                    logger.warning(f"Bot doesn't have delete permission in chat {chat_id}")
                    return chat_stats
            
            # Calculate cutoff times (when messages should be deleted)
            current_time = datetime.now()
            user_cutoff = current_time - timedelta(minutes=self.user_messages_threshold)
            all_cutoff = current_time - timedelta(minutes=self.all_messages_threshold)
            
            # Get messages to process
            # In a real implementation, we'd use Telegram API methods to get messages
            # Here we simulate by generating a list of message IDs
            # And then handling each message based on its properties
            
            # In reality, you'd need to use chat history methods to get messages
            # This is simplified and not using actual API due to API limitations
            message_ids = range(1, 1000)  # Placeholder for message IDs
            
            for msg_id in message_ids:
                chat_stats["total_messages"] += 1
                
                try:
                    # This is where we'd get the actual message from Telegram API
                    # For this simulated example, we'll decide based on the message ID
                    # In reality, we'd check:
                    # 1. Message date against thresholds
                    # 2. User ID against exceptions list
                    # 3. Message type for other criteria
                    
                    # Simulate checking if message should be deleted
                    should_delete = await self._should_delete_message(
                        chat_id, msg_id, user_cutoff, all_cutoff
                    )
                    
                    if should_delete == "exempt":
                        chat_stats["exempt_messages"] += 1
                        await self.db.log_deletion(msg_id, chat_id, "no", "Exempt user")
                        continue
                        
                    if should_delete == "skip":
                        chat_stats["skipped_messages"] += 1
                        await self.db.log_deletion(msg_id, chat_id, "no", "Not old enough")
                        continue
                    
                    # Delete the message if not dry run
                    if not self.dry_run:
                        await self.bot.delete_message(chat_id, msg_id)
                        chat_stats["deleted_messages"] += 1
                        await self.db.log_deletion(msg_id, chat_id, "yes")
                    else:
                        logger.info(f"[DRY RUN] Would delete message {msg_id} in chat {chat_id}")
                        chat_stats["deleted_messages"] += 1
                        await self.db.log_deletion(msg_id, chat_id, "dryrun")
                    
                except BadRequest as e:
                    # Handle message already deleted or can't be deleted
                    logger.warning(f"Couldn't delete message {msg_id} in {chat_id}: {str(e)}")
                    chat_stats["error_messages"] += 1
                    await self.db.log_deletion(msg_id, chat_id, "error", str(e))
                    
                except (Forbidden, NetworkError, TimedOut) as e:
                    # More serious errors
                    logger.error(f"Error deleting message {msg_id} in {chat_id}: {str(e)}")
                    chat_stats["error_messages"] += 1
                    await self.db.log_deletion(msg_id, chat_id, "error", str(e))
                    
                    # For some errors, we might want to stop processing this chat
                    if isinstance(e, Forbidden):
                        raise e
            
            return chat_stats
            
        except TelegramError as e:
            logger.error(f"Error accessing chat {chat_id}: {str(e)}")
            return chat_stats
      async def _should_delete_message(self, chat_id: int, message_id: int,
                                   user_cutoff: datetime, all_cutoff: datetime) -> str:
        """Determine if a message should be deleted based on rules.
        
        Args:
            chat_id: Telegram chat ID
            message_id: Telegram message ID
            user_cutoff: Datetime threshold for user messages
            all_cutoff: Datetime threshold for all messages
            
        Returns:
            str: "delete", "skip", or "exempt"
        """
        # In a real implementation, this would check the actual message
        # from the Telegram API. Here we simulate the logic.
        
        # NOTE: In a real implementation, you would:
        # 1. Get the actual message from Telegram API
        # 2. Check the message.from_user.id against exceptions
        # 3. Check if the message is from a channel and check channel ID against exceptions
        # 4. Check message date against thresholds
        
        # Simplified logic for demo purposes:
        # - Even IDs are "user" messages, odd IDs are "bot" messages
        # - First 10% of IDs are from "exempt" users
        # - Message date is simulated based on message ID
        
        is_bot_message = message_id % 2 == 1
        
        # Simulate checking for exempt users or channels
        # In a real implementation:
        # 1. For user messages: check if message.from_user.id in self.exceptions
        # 2. For channel messages: check if message.sender_chat.id in self.exceptions
        
        # This is just a simulation - in reality you'd check the actual message source
        is_exempt_user = message_id % 10 == 0
        is_from_exempt_channel = chat_id < 0 and abs(chat_id) in self.exceptions
        
        # Check if message is exempt (from exempt user or channel)
        if is_exempt_user or is_from_exempt_channel:
            logger.debug(f"Message {message_id} in chat {chat_id} is exempt from deletion")
            return "exempt"
        
        # Simulate message date (lower ID = older message)
        # This is just for demonstration
        if message_id < 300:  # Simulate old messages (beyond both thresholds)
            return "delete"
        elif message_id < 600:  # Simulate messages beyond user threshold but not all
            if is_bot_message:
                return "skip"
            return "delete"
        else:  # Simulate newer messages
            return "skip"
