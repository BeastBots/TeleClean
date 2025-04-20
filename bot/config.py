import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for the bot."""
    
    def __init__(self):
        # Telegram API credentials
        self.api_id = int(os.environ.get('TELEGRAM_API', 0))
        self.api_hash = os.environ.get('TELEGRAM_HASH', '')
        self.bot_token = os.environ.get('BOT_TOKEN', '')
        self.owner_id = int(os.environ.get('OWNER_ID', 0))
        
        # Timeout settings
        self.user_timeout = int(os.environ.get('USER_TIMEOUT', 900))  # Default 15 minutes in seconds
        self.bot_timeout = int(os.environ.get('BOT_TIMEOUT', 24))     # Default 24 hours
        
        # Exceptions
        self.exceptions_str = os.environ.get('EXCEPTIONS', '')
        self.exceptions = self._parse_exceptions()
        
    def _parse_exceptions(self):
        """Parse the exceptions string into a list of integers."""
        exceptions = []
        if self.exceptions_str:
            try:
                exceptions = [int(x.strip()) for x in self.exceptions_str.split(',')]
                logger.info(f"Exceptions loaded: {exceptions}")
            except ValueError:
                logger.error("Invalid EXCEPTIONS format. Use comma-separated integers.")
        return exceptions
    
    def validate(self):
        """Validate that all required configurations are set."""
        missing = []
        
        if not self.api_id:
            missing.append('TELEGRAM_API')
        if not self.api_hash:
            missing.append('TELEGRAM_HASH')
        if not self.bot_token:
            missing.append('BOT_TOKEN')
        if not self.owner_id:
            missing.append('OWNER_ID')
            
        return missing
    
    def update_user_timeout(self, timeout):
        """Update the user message timeout."""
        self.user_timeout = int(timeout)
        logger.info(f"User timeout updated to {self.user_timeout} seconds")
        
    def update_bot_timeout(self, timeout):
        """Update the bot message timeout."""
        self.bot_timeout = int(timeout)
        logger.info(f"Bot timeout updated to {self.bot_timeout} hours")

# Create a singleton config instance
config = Config() 