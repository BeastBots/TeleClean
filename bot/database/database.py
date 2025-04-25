#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database interface for TeleClean bot.
Handles connections to MongoDB and provides database operations.
"""

import asyncio
from typing import Dict, List, Any, Optional, Union
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger


class Database:
    """MongoDB database interface for TeleClean."""
    
    def __init__(self, mongo_uri: str):
        """Initialize database connection.
        
        Args:
            mongo_uri: MongoDB connection URI
        """
        try:
            # Connect to MongoDB with a timeout
            self.client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client.TeleClean
            
            # Collections
            self.botpm = self.db.records.botpm
            self.chats = self.db.records.chats
            self.channels = self.db.records.channels
            self.interaction_history = self.db.history.interaction
            self.deletion_history = self.db.history.deletion
            
            logger.info("MongoDB connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {str(e)}")
            # Re-raise the exception to allow proper error handling at a higher level
            raise
    
    async def validate_connection(self) -> bool:
        """Validate that the MongoDB connection is working.
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            # Attempt a simple operation to verify connection
            # The ping command is lightweight and ideal for checking connectivity
            await self.client.admin.command('ping')
            logger.info("MongoDB connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection validation failed: {str(e)}")
            return False
    
    async def setup_collections(self):
        """Set up required collections and indexes."""
        try:
            # No need to create indexes on _id fields as they're already indexed by default
            
            # Create secondary indexes for date-based operations
            await self.interaction_history.create_index("date")
            await self.deletion_history.create_index("date")
            
            # Create other useful indexes
            await self.botpm.create_index("active")
            await self.chats.create_index("active")
            await self.channels.create_index("active")
            
            logger.info("Database collections and indexes set up")
        except Exception as e:
            logger.error(f"Error setting up database collections and indexes: {str(e)}")
            # Continue execution even if index creation fails
            # This allows the bot to function with possibly degraded performance
            # rather than failing completely
    
    async def add_chat(self, chat_id: int, chat_type: str = "group") -> bool:
        """Add a chat to the database.
        
        Args:
            chat_id: Telegram chat ID
            chat_type: Type of chat (group, supergroup, channel, private)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            collection = self._get_collection_for_chat_type(chat_type)
            if collection is None:
                logger.error(f"Invalid chat type: {chat_type}")
                return False
            
            # Insert or update the chat record
            await collection.update_one(
                {"_id": chat_id},
                {"$set": {"active": True}},
                upsert=True
            )
            
            # Log the interaction
            await self.interaction_history.insert_one({
                "id": chat_id,
                "action": "joined",
                "type": chat_type,
                "date": asyncio.get_event_loop().time()
            })
            
            logger.info(f"Added {chat_type} with ID {chat_id} to database")
            return True
        except Exception as e:
            logger.error(f"Failed to add chat {chat_id} to database: {str(e)}")
            return False
    
    async def remove_chat(self, chat_id: int, chat_type: str = "group") -> bool:
        """Remove a chat from the database.
        
        Args:
            chat_id: Telegram chat ID
            chat_type: Type of chat (group, supergroup, channel, private)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            collection = self._get_collection_for_chat_type(chat_type)
            if collection is None:
                logger.error(f"Invalid chat type: {chat_type}")
                return False
            
            # Mark the chat as inactive
            await collection.update_one(
                {"_id": chat_id},
                {"$set": {"active": False}}
            )
            
            # Log the interaction
            await self.interaction_history.insert_one({
                "id": chat_id,
                "action": "left",
                "type": chat_type,
                "date": asyncio.get_event_loop().time()
            })
            
            logger.info(f"Removed {chat_type} with ID {chat_id} from database")
            return True
        except Exception as e:
            logger.error(f"Failed to remove chat {chat_id} from database: {str(e)}")
            return False
    
    async def get_all_active_chats(self) -> List[Dict[str, Any]]:
        """Get all active chats.
        
        Returns:
            list: List of chat dictionaries
        """
        try:
            # Get chats from both collections
            group_chats = await self.chats.find({"active": True}).to_list(None)
            channel_chats = await self.channels.find({"active": True}).to_list(None)
            all_chats = group_chats + channel_chats
            
            logger.info(f"Retrieved {len(all_chats)} active chats")
            return all_chats
        except Exception as e:
            logger.error(f"Failed to get active chats: {str(e)}")
            return []
    
    async def log_deletion(self, message_id: int, chat_id: int, 
                          deleted: str, reason: str = None) -> bool:
        """Log a deletion attempt.
        
        Args:
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            deleted: "yes", "no", "dryrun", or "error"
            reason: Reason for not deleting or error
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create log entry
            log_entry = {
                "message_id": message_id,
                "chat_id": chat_id,
                "deleted": deleted,
                "date": asyncio.get_event_loop().time()
            }
            
            # Add reason if provided
            if reason:
                log_entry["reason"] = reason
            
            # Insert log entry
            await self.deletion_history.insert_one(log_entry)
            return True
        except Exception as e:
            logger.error(f"Failed to log deletion: {str(e)}")
            return False
    
    def _get_collection_for_chat_type(self, chat_type: str):
        """Get the appropriate collection for the chat type.
        
        Args:
            chat_type: Type of chat (group, supergroup, channel, private)
            
        Returns:
            Collection object or None if invalid type
        """
        if chat_type in ["group", "supergroup"]:
            return self.chats
        elif chat_type == "channel":
            return self.channels
        elif chat_type == "private":
            return self.botpm
        else:
            return None
    
    async def close(self):
        """Close the database connection."""
        if hasattr(self, 'client') and self.client is not None:
            self.client.close()
            logger.info("MongoDB connection closed")
