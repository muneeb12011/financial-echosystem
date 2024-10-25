import unittest
from unittest.mock import patch, MagicMock
from modules.api_integration import APIIntegration

class TestAPIIntegration(unittest.TestCase):
    
    @patch('modules.api_integration.requests.post')
    def test_send_payment_success(self, mock_post):
        # Mocking a successful payment response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'data': {'id': '12345'}}
        mock_post.return_value = mock_response

        response = APIIntegration.send_payment('venmo', 100)

        self.assertEqual(response['status'], 'success')
        self.assertIn('data', response)

    @patch('modules.api_integration.requests.post')
    def test_send_payment_failure(self, mock_post):
        # Mocking a failed payment response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'status': 'error', 'message': 'Insufficient funds'}
        mock_post.return_value = mock_response

        response = APIIntegration.send_payment('venmo', 100)

        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'Insufficient funds')

    @patch('modules.api_integration.requests.post')
    def test_send_payment_invalid_account(self, mock_post):
        # Mocking a call to an unsupported account type
        with self.assertRaises(ValueError):
            APIIntegration.send_payment('invalid_account', 100)

    @patch('modules.api_integration.requests.post')
    def test_send_payment_network_error(self, mock_post):
        # Mocking a network error
        mock_post.side_effect = Exception("Network error")
        
        response = APIIntegration.send_payment('venmo', 100)

        self.assertEqual(response['status'], 'error')
        self.assertIn('message', response)
        self.assertEqual(response['message'], "Network error")

if __name__ == "__main__":
    unittest.main()
