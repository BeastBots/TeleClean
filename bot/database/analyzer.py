#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database analyzer for TeleClean bot.
Scans and cleans invalid chat records.
"""

from typing import Dict, List, Any, Tuple
import asyncio
from loguru import logger
from telegram.ext import Application
from telegram.error import (
    BadRequest, Forbidden, NetworkError, ChatMigrated, TimedOut
)

from bot.database.database import Database


class DatabaseAnalyzer:
    """Handles analysis and cleaning of database records."""
    
    def __init__(self, app: Application, db: Database):
        """Initialize the analyzer.
        
        Args:
            app: Telegram Application instance
            db: Database instance
        """
        self.app = app
        self.db = db
        self.bot = app.bot
        logger.info("Database analyzer initialized")
    
    async def verify_chat_records(self) -> Tuple[int, int]:
        """Verify that all stored chats are still valid.
        
        Checks if bot is still a member/admin of all chats in database.
        
        Returns:
            tuple: (number of valid chats, number of removed chats)
        """
        logger.info("Starting chat records verification")
        all_chats = await self.db.get_all_active_chats()
        
        valid_count = 0
        removed_count = 0
        
        for chat in all_chats:
            chat_id = chat.get("_id")
            chat_type = chat.get("type", "group")
            
            try:
                # Try to get chat information to verify bot's membership
                chat_obj = await self.bot.get_chat(chat_id)
                
                # If the chat type has changed, update it
                if chat_type != chat_obj.type:
                    logger.info(f"Chat type changed for {chat_id}: "
                               f"{chat_type} -> {chat_obj.type}")
                    # Mark old record as inactive
                    await self.db.remove_chat(chat_id, chat_type)
                    # Add new record with correct type
                    await self.db.add_chat(chat_id, chat_obj.type)
                
                # For groups and channels, check if bot is admin
                if chat_obj.type in ["group", "supergroup", "channel"]:
                    bot_member = await chat_obj.get_member(self.bot.id)
                    if not bot_member.status in ["administrator", "creator"]:
                        logger.warning(f"Bot is not admin in {chat_id}, "
                                      f"removing record")
                        await self.db.remove_chat(chat_id, chat_obj.type)
                        removed_count += 1
                        continue
                
                valid_count += 1
                
            except (BadRequest, Forbidden) as e:
                # Bot was kicked or banned
                logger.warning(f"Bot no longer in chat {chat_id}: {str(e)}")
                await self.db.remove_chat(chat_id, chat_type)
                removed_count += 1
                
            except ChatMigrated as e:
                # Supergroup migration case
                new_chat_id = e.new_chat_id
                logger.info(f"Chat {chat_id} migrated to {new_chat_id}")
                
                # Remove old record
                await self.db.remove_chat(chat_id, chat_type)
                
                # Add new record
                try:
                    chat_obj = await self.bot.get_chat(new_chat_id)
                    await self.db.add_chat(new_chat_id, chat_obj.type)
                    valid_count += 1
                except Exception as inner_e:
                    logger.error(f"Failed to add migrated chat: {str(inner_e)}")
                    removed_count += 1
                    
            except (NetworkError, TimedOut) as e:
                # Network errors - don't remove the chat but log the issue
                logger.error(f"Network error verifying chat {chat_id}: {str(e)}")
                valid_count += 1  # Consider it valid for now
                
            except Exception as e:
                logger.error(f"Unexpected error verifying chat {chat_id}: {str(e)}")
                await self.db.remove_chat(chat_id, chat_type)
                removed_count += 1
        
        logger.info(f"Chat verification complete: {valid_count} valid, "
                   f"{removed_count} removed")
        return (valid_count, removed_count)
    
    async def clean_stale_records(self) -> int:
        """Remove any records that are marked as inactive for over 30 days.
        
        Returns:
            int: Number of cleaned records
        """
        # This is a placeholder for actual implementation
        # In a real application, you would check the timestamp of when
        # a record was marked inactive and delete it if it's beyond
        # a certain threshold
        
        logger.info("Cleaning stale database records")
        cleaned_count = 0
        
        # Actual implementation would go here
        
        logger.info(f"Stale record cleaning complete: {cleaned_count} removed")
        return cleaned_count
