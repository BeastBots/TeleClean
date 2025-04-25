#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Alerts package for TeleClean bot.
Provides notification functionality for bot lifecycle events.
"""

from bot.alerts.start import StartAlert
from bot.alerts.update import UpdateAlert
from bot.alerts.stop import StopAlert
from bot.alerts.error import ErrorAlert
