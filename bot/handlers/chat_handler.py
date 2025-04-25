#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chat handler for TeleClean bot.
Tracks which chats/channels the bot is in.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from loguru import logger
from telegram import Update, Chat
from telegram.ext import ContextTypes, CommandHandler, ChatMemberHandler, filters
from telegram.error import BadRequest, Forbidden, TelegramError

from bot.database.database import Database


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command.
    
    This adds the chat to the database and provides welcome info.
    
    Args:
        update: Update object from telegram
        context: Context object from telegram
    """
    if not update.effective_chat:
        return
    
    chat = update.effective_chat
    chat_id = chat.id
    chat_type = chat.type
    
    # Add chat to database
    db: Database = context.bot_data.get("db")
    if db:
        await db.add_chat(chat_id, chat_type)
    
    # Send welcome message
    if chat_type == "private":
        await update.effective_message.reply_text(
            "👋 Welcome to TeleClean Bot!\n\n"
            "I automatically clean messages in groups and channels based on time thresholds.\n\n"
            "To use me:\n"
            "1. Add me to your group/channel\n"
            "2. Make me an admin with 'Delete messages' permission\n"
            "3. I'll handle the rest!\n\n"
            "For more information, contact the bot owner."
        )
    else:
        await update.effective_message.reply_text(
            "👋 TeleClean Bot is now active in this chat!\n\n"
            "I'll automatically clean messages based on time thresholds.\n"
            "Make sure I have 'Delete messages' permission."
        )


async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle updates to chat members (bot added/removed).
    
    Args:
        update: Update object from telegram
        context: Context object from telegram
    """
    if not update.chat_member or not update.effective_chat:
        return
    
    chat = update.effective_chat
    chat_id = chat.id
    chat_type = chat.type
    db: Database = context.bot_data.get("db")
    
    if not db:
        logger.error("Database not initialized in chat_member_update")
        return
    
    # Get the bot's ID
    bot_id = context.bot.id
    
    # Check if the update is about the bot
    if update.chat_member.new_chat_member.user.id != bot_id:
        return
        
    # Bot was added to the chat
    if update.chat_member.new_chat_member.status in ["member", "administrator"]:
        logger.info(f"Bot was added to {chat_type} {chat_id}")
        await db.add_chat(chat_id, chat_type)
        
    # Bot was removed from the chat
    elif update.chat_member.new_chat_member.status in ["left", "kicked"]:
        logger.info(f"Bot was removed from {chat_type} {chat_id}")
        await db.remove_chat(chat_id, chat_type)


async def my_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle updates to the bot's chat member status.
    
    Args:
        update: Update object from telegram
        context: Context object from telegram
    """
    if not update.my_chat_member or not update.effective_chat:
        return
    
    chat = update.effective_chat
    chat_id = chat.id
    chat_type = chat.type
    db: Database = context.bot_data.get("db")
    
    if not db:
        logger.error("Database not initialized in my_chat_member_update")
        return
    
    # Bot was added to the chat
    if update.my_chat_member.new_chat_member.status in ["member", "administrator"]:
        logger.info(f"Bot was added to {chat_type} {chat_id}")
        await db.add_chat(chat_id, chat_type)
        
    # Bot was removed from the chat
    elif update.my_chat_member.new_chat_member.status in ["left", "kicked"]:
        logger.info(f"Bot was removed from {chat_type} {chat_id}")
        await db.remove_chat(chat_id, chat_type)


class ChatHandler:
    """Handles chat management and tracking."""
    
    def __init__(self, application):
        """Initialize the chat handler.
        
        Args:
            application: Telegram Application instance
        """
        self.app = application
        self.bot = application.bot
        self.db: Database = application.bot_data.get("db")
        
        # Register handlers
        self.app.add_handler(CommandHandler("start", start_command))
        self.app.add_handler(ChatMemberHandler(chat_member_update, ChatMemberHandler.ANY_CHAT_MEMBER))
        self.app.add_handler(ChatMemberHandler(my_chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
        
        logger.info("Chat handler initialized")
    
    async def sync_chats(self) -> Tuple[int, int, int]:
        """Verify and sync all chats where the bot is a member.
        
        Returns:
            tuple: (total chats, added chats, removed chats)
        """
        logger.info("Starting chat sync process")
        
        if not self.db:
            logger.error("Database not initialized in sync_chats")
            return (0, 0, 0)
        
        # Get all chats from database
        db_chats = await self.db.get_all_active_chats()
        db_chat_ids = {chat["_id"] for chat in db_chats}
        
        added_count = 0
        removed_count = 0
        
        # Check if bot is still in these chats
        for chat in db_chats:
            chat_id = chat["_id"]
            chat_type = chat["type"]
            
            try:
                # Try to get chat info to verify membership
                chat_obj = await self.bot.get_chat(chat_id)
                
                # For groups and channels, check if bot is admin
                if chat_obj.type in ["group", "supergroup", "channel"]:
                    try:
                        bot_member = await chat_obj.get_member(self.bot.id)
                        if bot_member.status not in ["administrator", "creator"]:
                            logger.warning(f"Bot is not admin in {chat_id}, skipping")
                            # Don't remove, just log the issue
                    except (BadRequest, Forbidden) as e:
                        logger.warning(f"Cannot check admin status in {chat_id}: {str(e)}")
                        await self.db.remove_chat(chat_id, chat_type)
                        removed_count += 1
            
            except (BadRequest, Forbidden) as e:
                logger.warning(f"Bot is no longer in chat {chat_id}: {str(e)}")
                await self.db.remove_chat(chat_id, chat_type)
                removed_count += 1
                
            except TelegramError as e:
                logger.error(f"Error checking chat {chat_id}: {str(e)}")
        
        total_chats = len(db_chat_ids) - removed_count + added_count
        logger.info(f"Chat sync complete: {total_chats} total, "
                   f"{added_count} added, {removed_count} removed")
        
        return (total_chats, added_count, removed_count)
    
    async def get_active_chats(self) -> List[Dict[str, Any]]:
        """Get all active chats from the database.
        
        Returns:
            list: List of chat documents
        """
        if not self.db:
            logger.error("Database not initialized in get_active_chats")
            return []
        
        return await self.db.get_all_active_chats()
