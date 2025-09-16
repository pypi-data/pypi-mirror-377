"""
Teams Webhook Package
A simple Python package to send messages to Microsoft Teams using webhooks.
"""

from .teams_webhook import TeamsWebhook, send_teams_message

__version__ = "1.0.0"
__author__ = "Pandiyaraj Karuppasamy"
__email__ = "pandiyarajk@live.com"

__all__ = ["TeamsWebhook", "send_teams_message"]
