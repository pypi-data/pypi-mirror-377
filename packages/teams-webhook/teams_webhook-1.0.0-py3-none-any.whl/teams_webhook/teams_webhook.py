"""
Teams Webhook Package
A simple Python package to send messages to Microsoft Teams using webhooks.
"""

import requests
import json
from typing import Optional


class TeamsWebhook:
    """
    A class to send messages to Microsoft Teams using webhooks.
    """
    
    def __init__(self, webhook_url: str):
        """
        Initialize the TeamsWebhook with a webhook URL.
        
        Args:
            webhook_url (str): The Microsoft Teams webhook URL
        """
        self.webhook_url = webhook_url
    
    def send_message(self, 
                    message_title: str,
                    activity_title: str,
                    activity_subtitle: str,
                    text_message: str,
                    theme_color: str = "0076D7",
                    activity_image: Optional[str] = None) -> dict:
        """
        Send a message to Microsoft Teams.
        
        Args:
            message_title (str): The main title of the message
            activity_title (str): The activity title in the message card
            activity_subtitle (str): The activity subtitle in the message card
            text_message (str): The main text content of the message
            theme_color (str, optional): The theme color of the message card. Defaults to "0076D7" (blue)
            activity_image (str, optional): URL of the activity image. Defaults to None
            
        Returns:
            dict: Response dictionary with success status and details
        """
        # Create the message payload
        message = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": message_title,
            "themeColor": theme_color,
            "title": message_title,
            "text": text_message,
            "sections": [{
                "activityTitle": activity_title,
                "activitySubtitle": activity_subtitle
            }]
        }
        
        # Add activity image if provided
        if activity_image:
            message["sections"][0]["activityImage"] = activity_image
        
        try:
            # Send POST request to Teams
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # Check response
            if response.status_code in [200, 202]:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "message": "Message sent successfully to Microsoft Teams!",
                    "response": response.text
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"Failed to send message: {response.status_code}",
                    "response": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "status_code": None,
                "message": f"Request failed: {str(e)}",
                "response": None
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "message": f"Unexpected error: {str(e)}",
                "response": None
            }


def send_teams_message(webhook_url: str,
                      message_title: str,
                      activity_title: str,
                      activity_subtitle: str,
                      text_message: str,
                      theme_color: str = "0076D7",
                      activity_image: Optional[str] = None) -> dict:
    """
    Convenience function to send a message to Microsoft Teams.
    
    Args:
        webhook_url (str): The Microsoft Teams webhook URL
        message_title (str): The main title of the message
        activity_title (str): The activity title in the message card
        activity_subtitle (str): The activity subtitle in the message card
        text_message (str): The main text content of the message
        theme_color (str, optional): The theme color of the message card. Defaults to "0076D7" (blue)
        activity_image (str, optional): URL of the activity image. Defaults to None
        
    Returns:
        dict: Response dictionary with success status and details
    """
    webhook = TeamsWebhook(webhook_url)
    return webhook.send_message(
        message_title=message_title,
        activity_title=activity_title,
        activity_subtitle=activity_subtitle,
        text_message=text_message,
        theme_color=theme_color,
        activity_image=activity_image
    )
