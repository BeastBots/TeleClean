#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GitHub Actions entry script for TeleClean bot.
Verifies environment and starts the deletion process.
"""

import os
import sys
import logging
from loguru import logger


def verify_env():
    """Verify that all required environment variables are set."""
    required_vars = [
        "BOT_TOKEN",
        "MONGO_URI",
        "OWNER_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Verify MongoDB URI format
    mongo_uri = os.environ.get("MONGO_URI", "")
    if mongo_uri and not mongo_uri.startswith(("mongodb://", "mongodb+srv://")):
        logger.error("Invalid MONGO_URI format. Must start with 'mongodb://' or 'mongodb+srv://'")
        return False
    
    return True


def main():
    """Main entry point for GitHub Actions."""
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info("Starting TeleClean in GitHub Actions environment")
    
    # Verify environment
    if not verify_env():
        sys.exit(1)
      # Import and run main process
    try:
        from main import main as run_main
        run_main()
    except ImportError as e:
        logger.error(f"Failed to import main module: {str(e)}")
        sys.exit(1)
    except ConnectionError as e:
        logger.error(f"Database connection error: {str(e)}")
        # MongoDB connection issues exit with specific error code
        sys.exit(2)
    except Exception as e:
        logger.error(f"Error running main process: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
