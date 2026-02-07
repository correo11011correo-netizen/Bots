import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root directory to sys.path to allow importing 'botones_core'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from botones_core import send_test_buttons, load_config

class TestButtonsPayload(unittest.TestCase):

    def setUp(self):
        # Mock load_config to return a dummy config for testing
        self.mock_config = {
            'whatsapp_business_api_token': 'dummy_token',
            'whatsapp_business_phone_id': 'dummy_phone_id',
            'verify_token': 'dummy_verify_token'
        }
        self.recipient_id = "test_recipient_id"

        # Define the expected payload structure for buttons
        self.expected_payload = {
            "messaging_product": "whatsapp",
            "to": self.recipient_id,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Elige una opción:"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "btn1", "title": "Ver menú"}},
                        {"type": "reply", "reply": {"id": "btn2", "title": "Promoción"}},
                        {"type": "reply", "reply": {"id": "btn3", "title": "Contacto"}}
                    ]
                }
            }
        }

    @patch('botones_core.requests.post')
    @patch('botones_core.load_config')
    def test_send_test_buttons_payload(self, mock_load_config, mock_requests_post):
        """
        Test that send_test_buttons constructs and sends the correct payload for buttons.
        """
        mock_load_config.return_value = self.mock_config
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        # Call the function under test
        send_test_buttons(self.mock_config, self.recipient_id)

        # Assert that requests.post was called
        mock_requests_post.assert_called_once()

        # Get the arguments with which requests.post was called
        _args, kwargs = mock_requests_post.call_args

        # Assert the URL
        expected_url = (f"https://graph.facebook.com/v19.0/"
                        f"{self.mock_config['whatsapp_business_phone_id']}/messages")
        self.assertEqual(_args[0], expected_url)

        # Assert the headers
        expected_headers = {
            "Authorization": f"Bearer {self.mock_config['whatsapp_business_api_token']}",
            "Content-Type": "application/json"
        }
        self.assertEqual(kwargs['headers'], expected_headers)

        # Assert the JSON payload
        self.assertDictEqual(kwargs['json'], self.expected_payload)

class TestLinksPayload(unittest.TestCase):

    def setUp(self):
        # Mock load_config to return a dummy config for testing
        self.mock_config = {
            'whatsapp_business_api_token': 'dummy_token',
            'whatsapp_business_phone_id': 'dummy_phone_id',
            'verify_token': 'dummy_verify_token'
        }
        self.recipient_id = "test_recipient_id"

        # Define the expected payload structure for links (as a text message)
        self.expected_payload = {
            "messaging_product": "whatsapp",
            "to": self.recipient_id,
            "type": "text",
            "text": {"body": "Visita nuestro sitio web: https://tusitio.com"}
        }

    @patch('botones_core.requests.post')
    @patch('botones_core.load_config')
    def test_send_test_link_payload(self, mock_load_config, mock_requests_post):
        """
        Test that send_test_link constructs and sends the correct payload for a link.
        """
        mock_load_config.return_value = self.mock_config
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        # Call the function under test
        from botones_core import send_test_link # Import here to avoid circular dependency if placed at top
        send_test_link(self.mock_config, self.recipient_id)

        # Assert that requests.post was called
        mock_requests_post.assert_called_once()

        # Get the arguments with which requests.post was called
        _args, kwargs = mock_requests_post.call_args

        # Assert the URL
        expected_url = (f"https://graph.facebook.com/v19.0/"
                        f"{self.mock_config['whatsapp_business_phone_id']}/messages")
        self.assertEqual(_args[0], expected_url)

        # Assert the headers
        expected_headers = {
            "Authorization": f"Bearer {self.mock_config['whatsapp_business_api_token']}",
            "Content-Type": "application/json"
        }
        self.assertEqual(kwargs['headers'], expected_headers)

        # Assert the JSON payload
        self.assertDictEqual(kwargs['json'], self.expected_payload)

if __name__ == '__main__':
    unittest.main()

