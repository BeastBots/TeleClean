#!/usr/bin/env python3
import sys
import logging
import dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to start the TG Auto Deletion Bot.
    """
    logger.info("Starting TG Auto Deletion Bot...")
    
    # Load environment variables from config.env
    try:
        dotenv.load_dotenv("config.env")
        logger.info("Environment variables loaded from config.env")
    except Exception as e:
        logger.error(f"Failed to load environment variables: {e}")
        sys.exit(1)
    
    # Import configuration and validate
    try:
        from bot.config import config
        
        # Verify required environment variables
        missing_vars = config.validate()
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please set them in config.env file")
            sys.exit(1)
            
        logger.info("Configuration validated successfully")
    except ImportError:
        logger.error("Failed to import config module. Make sure the bot directory exists and contains config.py")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        sys.exit(1)
    
    # Import and run the bot
    try:
        from bot.bot import main as bot_main
        import asyncio
        asyncio.run(bot_main())
    except ImportError:
        logger.error("Failed to import bot module. Make sure the bot directory exists and contains bot.py")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running the bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 