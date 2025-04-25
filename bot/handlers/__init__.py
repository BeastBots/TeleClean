#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Handlers package for TeleClean bot.
Provides message handlers and core bot functionality.
"""

from bot.handlers.config_handler import ConfigHandler
from bot.handlers.chat_handler import ChatHandler, start_command
from bot.handlers.error import ErrorHandler
from bot.handlers.executor import Executor
from bot.handlers.handlers import setup_handlers
