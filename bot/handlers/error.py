#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Error handler for TeleClean bot.
Custom error handler for telegram bot exceptions.
"""

import html
import traceback
import asyncio
from typing import Optional, Callable, Awaitable
from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.error import (
    BadRequest, Forbidden, NetworkError, TimedOut, TelegramError
)

from config import OWNER_ID


class ErrorHandler:
    """Custom error handler for the bot."""
    
    def __init__(self, owner_id: int):
        """Initialize error handler.
        
        Args:
            owner_id: Telegram user ID of the bot owner
        """
        self.owner_id = owner_id
        logger.info("Error handler initialized")
    
    async def handle_error(self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unexpected errors in the bot.
        
        Sends a detailed error message to the bot owner.
        
        Args:
            update: Update object from telegram (may be None)
            context: Context object from telegram
        """
        # Get the exception info
        error = context.error
        
        # Log the error
        logger.error(f"Exception while handling an update: {str(error)}")
        logger.error(f"{traceback.format_exc()}")
        
        # Handle specific known errors
        if isinstance(error, BadRequest):
            await self._handle_bad_request(update, context, error)
            return
            
        if isinstance(error, Forbidden):
            await self._handle_forbidden(update, context, error)
            return
            
        if isinstance(error, NetworkError) or isinstance(error, TimedOut):
            await self._handle_network_error(update, context, error)
            return
        
        # Prepare and send traceback to owner
        tb_list = traceback.format_exception(None, error, error.__traceback__)
        tb_string = "".join(tb_list)
        
        # Format the error message
        update_str = update.to_dict() if update else "No update"
        message = (
            f"❗ <b>An error occurred:</b>\n\n"
            f"<b>Exception:</b> {html.escape(str(error))}\n\n"
            f"<b>Update:</b>\n<pre>{html.escape(str(update_str))}</pre>\n\n"
            f"<b>Traceback:</b>\n<pre>{html.escape(tb_string)}</pre>"
        )
        
        # Split message if it's too long
        if len(message) > 4096:
            message = message[:4093] + "..."
        
        # Send error message to owner
        try:
            await context.bot.send_message(
                chat_id=self.owner_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send error message to owner: {str(e)}")
    
    async def _handle_bad_request(self, update: Optional[Update], 
                                context: ContextTypes.DEFAULT_TYPE, 
                                error: BadRequest) -> None:
        """Handle BadRequest errors.
        
        Args:
            update: Update object from telegram (may be None)
            context: Context object from telegram
            error: The error that occurred
        """
        error_message = str(error).lower()
        
        # Handle specific bad request errors
        if "message to delete not found" in error_message:
            # Message already deleted, just log and ignore
            logger.warning("Attempted to delete a message that was already deleted")
            return
            
        if "message can't be deleted" in error_message:
            # Can't delete, just log
            logger.warning("No permission to delete a message")
            return
            
        if "chat not found" in error_message:
            # Chat no longer exists or bot was kicked
            if update and update.effective_chat:
                # Remove chat from database
                db = context.bot_data.get("db")
                if db:
                    await db.remove_chat(
                        update.effective_chat.id,
                        update.effective_chat.type
                    )
            return
        
        # For other BadRequest errors, send to owner
        if update:
            chat_info = f" in chat {update.effective_chat.id}" if update.effective_chat else ""
            
            await context.bot.send_message(
                chat_id=self.owner_id,
                text=f"❗ <b>Bad Request Error{chat_info}:</b>\n{html.escape(str(error))}",
                parse_mode=ParseMode.HTML
            )
    
    async def _handle_forbidden(self, update: Optional[Update], 
                               context: ContextTypes.DEFAULT_TYPE, 
                               error: Forbidden) -> None:
        """Handle Forbidden errors.
        
        Args:
            update: Update object from telegram (may be None)
            context: Context object from telegram
            error: The error that occurred
        """
        # Typically happens when bot doesn't have permissions
        if update and update.effective_chat:
            logger.warning(f"Permission denied in chat {update.effective_chat.id}: {str(error)}")
            
            # Check if it's related to deletion permissions
            if "delete message" in str(error).lower():
                # Notify owner about permission issues
                await context.bot.send_message(
                    chat_id=self.owner_id,
                    text=(
                        f"⚠️ <b>Permission Issue:</b>\n"
                        f"I don't have permission to delete messages in "
                        f"chat <code>{update.effective_chat.id}</code> "
                        f"({html.escape(update.effective_chat.title)})"
                    ),
                    parse_mode=ParseMode.HTML
                )
    
    async def _handle_network_error(self, update: Optional[Update], 
                                   context: ContextTypes.DEFAULT_TYPE, 
                                   error: TelegramError) -> None:
        """Handle NetworkError and TimedOut errors.
        
        Args:
            update: Update object from telegram (may be None)
            context: Context object from telegram
            error: The error that occurred
        """
        # For network errors, just log and potentially retry later
        logger.error(f"Network error: {str(error)}")
        
        # Wait a bit before retrying
        await asyncio.sleep(2)
        
        # For critical operations, you might want to implement retry logic here
        
        # Notify owner if there are persistent network issues
        if context.bot_data.get("network_error_count", 0) > 5:
            await context.bot.send_message(
                chat_id=self.owner_id,
                text=f"⚠️ <b>Persistent Network Issues:</b>\n{html.escape(str(error))}",
                parse_mode=ParseMode.HTML
            )
            # Reset counter
            context.bot_data["network_error_count"] = 0
        else:
            # Increment counter
            context.bot_data["network_error_count"] = context.bot_data.get("network_error_count", 0) + 1

    def register_handlers(self, application) -> None:
        """Register the error handler with the application.
        
        Args:
            application: Telegram Application instance
        """
        application.add_error_handler(self.handle_error)
        logger.info("Error handler registered with application")
