import logging
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerUser

from bot.config import config
from bot.handlers import CommandHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Message tracking
user_messages = {}
bot_messages = {}

# The client will be initialized in the main function
client = None

@events.register(events.NewMessage)
async def handle_new_message(event):
    """Handle new messages and schedule them for deletion."""
    try:
        message = event.message
        chat_id = event.chat_id
        msg_id = message.id
        sender_id = None

        # Get sender ID
        if message.sender:
            if isinstance(message.sender, PeerUser):
                sender_id = message.sender.user_id
            elif hasattr(message.sender, 'id'):
                sender_id = message.sender.id

        # Check if sender is in exceptions list
        if sender_id in config.exceptions or chat_id in config.exceptions:
            logger.info(f"Message {msg_id} from {sender_id} in {chat_id} is excepted from deletion")
            return

        # Determine if it's a bot message or user message
        is_bot = message.via_bot or (hasattr(message.sender, 'bot') and message.sender.bot)
        
        if is_bot:
            # Schedule bot message deletion
            deletion_time = datetime.now() + timedelta(hours=config.bot_timeout)
            if chat_id not in bot_messages:
                bot_messages[chat_id] = {}
            bot_messages[chat_id][msg_id] = deletion_time
            logger.info(f"Bot message {msg_id} in {chat_id} scheduled for deletion at {deletion_time}")
        else:
            # Schedule user message deletion
            deletion_time = datetime.now() + timedelta(seconds=config.user_timeout)
            if chat_id not in user_messages:
                user_messages[chat_id] = {}
            user_messages[chat_id][msg_id] = deletion_time
            logger.info(f"User message {msg_id} in {chat_id} scheduled for deletion at {deletion_time}")
            
    except Exception as e:
        logger.error(f"Error in handle_new_message: {e}")

async def deletion_task():
    """Periodically check and delete messages that have reached their timeout."""
    global client
    
    while True:
        try:
            if client is None:
                logger.error("Client not initialized, cannot run deletion task")
                return
                
            current_time = datetime.now()
            
            # Check user messages
            for chat_id in list(user_messages.keys()):
                for msg_id in list(user_messages[chat_id].keys()):
                    if current_time >= user_messages[chat_id][msg_id]:
                        try:
                            await client.delete_messages(chat_id, msg_id)
                            logger.info(f"Deleted user message {msg_id} from {chat_id}")
                        except Exception as e:
                            logger.error(f"Failed to delete user message {msg_id} from {chat_id}: {e}")
                        del user_messages[chat_id][msg_id]
                
                # Clean up empty chat entries
                if not user_messages[chat_id]:
                    del user_messages[chat_id]
            
            # Check bot messages
            for chat_id in list(bot_messages.keys()):
                for msg_id in list(bot_messages[chat_id].keys()):
                    if current_time >= bot_messages[chat_id][msg_id]:
                        try:
                            await client.delete_messages(chat_id, msg_id)
                            logger.info(f"Deleted bot message {msg_id} from {chat_id}")
                        except Exception as e:
                            logger.error(f"Failed to delete bot message {msg_id} from {chat_id}: {e}")
                        del bot_messages[chat_id][msg_id]
                
                # Clean up empty chat entries
                if not bot_messages[chat_id]:
                    del bot_messages[chat_id]
                    
        except Exception as e:
            logger.error(f"Error in deletion_task: {e}")
        
        # Run every minute
        await asyncio.sleep(60)

async def main():
    """Main function to start the bot."""
    global client
    
    # Initialize client
    client = TelegramClient('bot_session', config.api_id, config.api_hash)
    await client.start(bot_token=config.bot_token)
    
    # Register all handlers
    client.add_event_handler(handle_new_message)
    
    # Register command handlers
    command_handlers = CommandHandlers(client, user_messages, bot_messages)
    command_handlers.register_handlers()
    
    # Start the deletion task
    deletion_task_handle = asyncio.create_task(deletion_task())
    
    logger.info("Bot started")
    
    try:
        # Run the client until disconnected
        await client.run_until_disconnected()
    finally:
        # Ensure proper cleanup
        if not deletion_task_handle.done():
            deletion_task_handle.cancel()
            try:
                await deletion_task_handle
            except asyncio.CancelledError:
                pass
        
        if client.is_connected():
            await client.disconnect()

if __name__ == "__main__":
    # Start the main function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main()) 