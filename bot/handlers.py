from telethon import events
import logging

from bot.config import config

logger = logging.getLogger(__name__)

class CommandHandlers:
    """Command handlers for bot commands."""
    
    def __init__(self, client, user_messages, bot_messages):
        self.client = client
        self.user_messages = user_messages
        self.bot_messages = bot_messages
        
    def register_handlers(self):
        """Register all command handlers."""
        self.client.add_event_handler(self.start_command)
        self.client.add_event_handler(self.status_command)
        self.client.add_event_handler(self.set_timeout_command)
        self.client.add_event_handler(self.help_command)
        self.client.add_event_handler(self.clear_command)
        
    @events.register(events.NewMessage(pattern='/start', from_users=config.owner_id))
    async def start_command(self, event):
        """Handle start command from owner."""
        await event.respond("TG Auto Deletion Bot is running. Messages will be automatically deleted based on configured timeouts. Use /help to see available commands.")
    
    @events.register(events.NewMessage(pattern='/status', from_users=config.owner_id))
    async def status_command(self, event):
        """Handle status command from owner."""
        user_count = sum(len(msgs) for msgs in self.user_messages.values())
        bot_count = sum(len(msgs) for msgs in self.bot_messages.values())
        status_message = (
            f"🤖 **TG Auto Deletion Bot Status**\n\n"
            f"User messages queued: {user_count}\n"
            f"Bot messages queued: {bot_count}\n\n"
            f"User timeout: {config.user_timeout} seconds\n"
            f"Bot timeout: {config.bot_timeout} hours\n"
            f"Exceptions: {config.exceptions_str or 'None'}"
        )
        await event.respond(status_message)
    
    @events.register(events.NewMessage(pattern='/settimeout', from_users=config.owner_id))
    async def set_timeout_command(self, event):
        """Handle timeout configuration from owner."""
        try:
            args = event.message.text.split()[1:]
            if len(args) != 2:
                await event.respond("Usage: /settimeout [user|bot] [time]")
                return
            
            timeout_type, timeout_value = args
            
            if timeout_type.lower() == "user":
                config.update_user_timeout(timeout_value)
                await event.respond(f"User message timeout set to {config.user_timeout} seconds")
            elif timeout_type.lower() == "bot":
                config.update_bot_timeout(timeout_value)
                await event.respond(f"Bot message timeout set to {config.bot_timeout} hours")
            else:
                await event.respond("Invalid timeout type. Use 'user' or 'bot'")
        except Exception as e:
            await event.respond(f"Error: {str(e)}")
    
    @events.register(events.NewMessage(pattern='/help', from_users=config.owner_id))
    async def help_command(self, event):
        """Show help information."""
        help_text = (
            "**TG Auto Deletion Bot Commands**\n\n"
            "/start - Start the bot\n"
            "/status - Check bot status\n"
            "/settimeout [user|bot] [time] - Set deletion timeout\n"
            "/clear [user|bot] - Clear message queue\n"
            "/help - Show this help message"
        )
        await event.respond(help_text)
    
    @events.register(events.NewMessage(pattern='/clear', from_users=config.owner_id))
    async def clear_command(self, event):
        """Clear message queue."""
        try:
            args = event.message.text.split()[1:]
            if not args:
                await event.respond("Usage: /clear [user|bot|all]")
                return
            
            queue_type = args[0].lower()
            
            if queue_type == "user":
                self.user_messages.clear()
                await event.respond("User message queue cleared")
            elif queue_type == "bot":
                self.bot_messages.clear()
                await event.respond("Bot message queue cleared")
            elif queue_type == "all":
                self.user_messages.clear()
                self.bot_messages.clear()
                await event.respond("All message queues cleared")
            else:
                await event.respond("Invalid queue type. Use 'user', 'bot', or 'all'")
        except Exception as e:
            await event.respond(f"Error: {str(e)}") 