#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration handler for TeleClean bot.
Loads configurations from environment variables or config file.
"""

import os
from typing import Dict, Any, List, Union
from loguru import logger


class ConfigHandler:
    """Handles loading and validation of bot configuration."""
    
    def __init__(self):
        """Initialize with default configurations."""
        self.config = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables or config.py.
        
        Returns:
            dict: Configuration dictionary
        """
        try:
            # Import configuration variables from config.py
            from config import (
                MONGO_URI, OWNER_ID, USER_MESSAGES, ALL_MESSAGES,
                EXCEPTIONS, DRY_RUN, BOT_TOKEN, UPDATE_INTERVAL, LOG_LEVEL
            )
            
            # Store configuration in dictionary
            self.config = {
                "mongo_uri": MONGO_URI,
                "owner_id": OWNER_ID,
                "user_messages": USER_MESSAGES,
                "all_messages": ALL_MESSAGES,
                "exceptions": EXCEPTIONS,
                "dry_run": DRY_RUN,
                "bot_token": BOT_TOKEN,
                "update_interval": UPDATE_INTERVAL,
                "log_level": LOG_LEVEL
            }
            
            # Validate required configurations
            self._validate_config()
            
            logger.info("Configuration loaded successfully")
            return self.config
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise ValueError("Failed to load configuration") from e
    
    def _validate_config(self):
        """Validate that all required configurations are present and valid."""
        # Check required fields
        required_fields = ["mongo_uri", "owner_id", "user_messages", 
                         "all_messages", "bot_token"]
        
        for field in required_fields:
            if not self.config.get(field):
                logger.error(f"Missing required configuration: {field}")
                raise ValueError(f"Missing required configuration: {field}")
        
        # Validate types
        if not isinstance(self.config["owner_id"], int):
            logger.error("owner_id must be an integer")
            raise ValueError("owner_id must be an integer")
            
        if not isinstance(self.config["user_messages"], int):
            logger.error("user_messages must be an integer")
            raise ValueError("user_messages must be an integer")
            
        if not isinstance(self.config["all_messages"], int):
            logger.error("all_messages must be an integer")
            raise ValueError("all_messages must be an integer")
            
        if not isinstance(self.config["exceptions"], list):
            logger.error("exceptions must be a list")
            raise ValueError("exceptions must be a list")
            
        # Validate values
        if self.config["user_messages"] <= 0:
            logger.warning("user_messages should be greater than 0, using default (60)")
            self.config["user_messages"] = 60
            
        if self.config["all_messages"] <= 0:
            logger.warning("all_messages should be greater than 0, using default (1440)")
            self.config["all_messages"] = 1440
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Get the entire configuration as a dictionary.
        
        Returns:
            dict: Configuration dictionary
        """
        return self.config.copy()
