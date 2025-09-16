"""
Test file for teams-webhook package
"""

import unittest
from unittest.mock import patch, Mock
from .teams_webhook import TeamsWebhook, send_teams_message


class TestTeamsWebhook(unittest.TestCase):
    """Test cases for TeamsWebhook class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.webhook_url = "https://test.webhook.office.com/webhookb2/test-url"
        self.webhook = TeamsWebhook(self.webhook_url)
    
    @patch('teams_webhook.teams_webhook.requests.post')
    def test_send_message_success(self, mock_post):
        """Test successful message sending"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_post.return_value = mock_response
        
        result = self.webhook.send_message(
            message_title="Test Title",
            activity_title="Test Activity",
            activity_subtitle="Test Subtitle",
            text_message="Test message"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 200)
        self.assertIn("successfully", result['message'])
    
    @patch('teams_webhook.teams_webhook.requests.post')
    def test_send_message_failure(self, mock_post):
        """Test failed message sending"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        result = self.webhook.send_message(
            message_title="Test Title",
            activity_title="Test Activity",
            activity_subtitle="Test Subtitle",
            text_message="Test message"
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 400)
        self.assertIn("Failed", result['message'])
    
    @patch('teams_webhook.teams_webhook.requests.post')
    def test_send_message_with_image(self, mock_post):
        """Test message sending with activity image"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_post.return_value = mock_response
        
        result = self.webhook.send_message(
            message_title="Test Title",
            activity_title="Test Activity",
            activity_subtitle="Test Subtitle",
            text_message="Test message",
            activity_image="https://example.com/image.png"
        )
        
        self.assertTrue(result['success'])
        # Verify the request was made with correct data
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        message_data = call_args[1]['data']
        self.assertIn('activityImage', message_data)


class TestSendTeamsMessage(unittest.TestCase):
    """Test cases for send_teams_message function"""
    
    @patch('teams_webhook.teams_webhook.TeamsWebhook')
    def test_send_teams_message_function(self, mock_webhook_class):
        """Test the convenience function"""
        # Mock the webhook instance
        mock_webhook_instance = Mock()
        mock_webhook_instance.send_message.return_value = {
            'success': True,
            'status_code': 200,
            'message': 'Success'
        }
        mock_webhook_class.return_value = mock_webhook_instance
        
        result = send_teams_message(
            webhook_url="https://test.webhook.office.com/webhookb2/test-url",
            message_title="Test Title",
            activity_title="Test Activity",
            activity_subtitle="Test Subtitle",
            text_message="Test message"
        )
        
        self.assertTrue(result['success'])
        mock_webhook_class.assert_called_once_with("https://test.webhook.office.com/webhookb2/test-url")
        mock_webhook_instance.send_message.assert_called_once()


if __name__ == '__main__':
    unittest.main()
