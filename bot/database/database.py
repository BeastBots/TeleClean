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
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client.TeleClean
        
        # Collections
        self.botpm = self.db.records.botpm
        self.chats = self.db.records.chats
        self.channels = self.db.records.channels
        self.interaction_history = self.db.history.interaction
        self.deletion_history = self.db.history.deletion
        
        logger.info("MongoDB connection initialized")
    
    async def setup_collections(self):
        """Set up required collections and indexes."""
        # Create indexes for faster lookups
        await self.botpm.create_index("_id", unique=True)
        await self.chats.create_index("_id", unique=True)
        await self.channels.create_index("_id", unique=True)
        await self.interaction_history.create_index("date")
        await self.deletion_history.create_index("date")
        
        logger.info("Database collections and indexes set up")
    
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
            
            # Mark the chat as inactive instead of deleting
            # This preserves history but indicates the bot is no longer in the chat
            await collection.update_one(
                {"_id": chat_id},
                {"$set": {"active": False}}
            )
            
            # Log the interaction
            await self.interaction_history.insert_one({
                "id": chat_id,
                "action": "removed",
                "type": chat_type,
                "date": asyncio.get_event_loop().time()
            })
            
            logger.info(f"Removed {chat_type} with ID {chat_id} from database")
            return True
        except Exception as e:
            logger.error(f"Failed to remove chat {chat_id} from database: {str(e)}")
            return False
    
    async def get_all_active_chats(self) -> List[Dict[str, Any]]:
        """Get all active chats where the bot is present.
        
        Returns:
            list: List of chat documents
        """
        try:
            # Gather all active chats from different collections
            private_chats = await self.botpm.find({"active": True}).to_list(None)
            group_chats = await self.chats.find({"active": True}).to_list(None)
            channel_chats = await self.channels.find({"active": True}).to_list(None)
            
            # Add chat type information to each document
            for chat in private_chats:
                chat["type"] = "private"
            for chat in group_chats:
                chat["type"] = "group"
            for chat in channel_chats:
                chat["type"] = "channel"
            
            all_chats = private_chats + group_chats + channel_chats
            logger.info(f"Retrieved {len(all_chats)} active chats from database")
            return all_chats
        except Exception as e:
            logger.error(f"Failed to retrieve active chats: {str(e)}")
            return []
    
    async def log_deletion(self, message_id: int, chat_id: int, 
                          result: str, error: Optional[str] = None) -> bool:
        """Log a message deletion attempt.
        
        Args:
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            result: 'yes' if deleted, 'no' if skipped, 'error' if failed
            error: Error message if result is 'error'
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            document = {
                "message_id": message_id,
                "chat_id": chat_id,
                "result": result,
                "date": asyncio.get_event_loop().time()
            }
            
            if error:
                document["error"] = error
                
            await self.deletion_history.insert_one(document)
            return True
        except Exception as e:
            logger.error(f"Failed to log deletion: {str(e)}")
            return False
    
    async def get_deletion_stats(self, 
                                hours: int = 24) -> Dict[str, Union[int, float]]:
        """Get deletion statistics for a specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            dict: Statistics about message deletions
        """
        try:
            # Calculate the timestamp for the cutoff
            current_time = asyncio.get_event_loop().time()
            cutoff_time = current_time - (hours * 3600)
            
            # Count the total deletions
            total_count = await self.deletion_history.count_documents({
                "date": {"$gte": cutoff_time}
            })
            
            # Count successful deletions
            success_count = await self.deletion_history.count_documents({
                "date": {"$gte": cutoff_time},
                "result": "yes"
            })
            
            # Count errors
            error_count = await self.deletion_history.count_documents({
                "date": {"$gte": cutoff_time},
                "result": "error"
            })
            
            # Count skipped
            skipped_count = await self.deletion_history.count_documents({
                "date": {"$gte": cutoff_time},
                "result": "no"
            })
            
            # Calculate success rate
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            
            return {
                "total": total_count,
                "success": success_count,
                "error": error_count,
                "skipped": skipped_count,
                "success_rate": success_rate
            }
        except Exception as e:
            logger.error(f"Failed to get deletion stats: {str(e)}")
            return {
                "total": 0,
                "success": 0,
                "error": 0,
                "skipped": 0,
                "success_rate": 0
            }
    
    def _get_collection_for_chat_type(self, chat_type: str):
        """Helper method to get the appropriate collection for a chat type.
        
        Args:
            chat_type: Type of chat (group, supergroup, channel, private)
            
        Returns:
            Collection object or None if invalid type
        """
        if chat_type in ["private", "bot"]:
            return self.botpm
        elif chat_type in ["group", "supergroup"]:
            return self.chats
        elif chat_type == "channel":
            return self.channels
        else:
            return None
    
    async def close(self):
        """Close the database connection."""
        self.client.close()
        logger.info("MongoDB connection closed")
