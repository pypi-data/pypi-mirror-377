"""
Example usage of the Teams Webhook Package
"""

from .teams_webhook import TeamsWebhook, send_teams_message

# Your webhook URL
webhook_url = "https://your-company.webhook.office.com/webhookb2/your-webhook-url"

def example_with_class():
    """Example using the TeamsWebhook class"""
    print("=== Using TeamsWebhook Class ===")
    
    webhook = TeamsWebhook(webhook_url)
    
    result = webhook.send_message(
        message_title="🚨 Error Alert",
        activity_title="Teams Webhook Bot", 
        activity_subtitle="Teams Webhook Automation",
        text_message="**Error Message:** Exception occurred while starting service<br>**Timestamp:** 2024-01-15 10:30:00<br>**System:** 192.168.1.100 WORKSTATION-01<br>**User:** John Doe"
    )
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['response']:
        print(f"Response: {result['response']}")

def example_with_function():
    """Example using the convenience function"""
    print("\n=== Using Convenience Function ===")
    
    result = send_teams_message(
        webhook_url=webhook_url,
        message_title="📊 Status Update",
        activity_title="System Monitor",
        activity_subtitle="Health Check",
        text_message="**Status:** All systems operational<br>**Uptime:** 99.9%<br>**Last Check:** 2024-01-15 10:35:00"
    )
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['response']:
        print(f"Response: {result['response']}")

def example_error_alert():
    """Example of an error alert message"""
    print("\n=== Error Alert Example ===")
    
    webhook = TeamsWebhook(webhook_url)
    
    result = webhook.send_message(
        message_title="🚨 Critical Error",
        activity_title="Error Monitor",
        activity_subtitle="Service Alert",
        text_message="**Error Level:** CRITICAL<br>**Service:** webapp-service<br>**Error:** Database connection failed<br>**Timestamp:** 2024-01-15 10:40:00<br>**Log File:** webapp-service.log",
        theme_color="FF0000",  # Red for error
        activity_image="https://www.python.org/static/community_logos/python-logo.png"
    )
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")

if __name__ == "__main__":
    # Run examples
    example_with_class()
    example_with_function() 
    example_error_alert()
