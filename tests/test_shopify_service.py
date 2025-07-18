import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.shopify_service import ShopifyService
from app.models.insights import Product, FAQ, SocialHandle


class TestShopifyService(unittest.TestCase):
    
    @patch('app.services.shopify_service.requests.Session')
    def setUp(self, mock_session):
        self.mock_session = MagicMock()
        mock_session.return_value = self.mock_session
        self.service = ShopifyService("https://example-store.myshopify.com")
    
    def test_get_products(self):
        # Mock the response for products.json
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "products": [
                {
                    "id": 123456789,
                    "title": "Test Product",
                    "handle": "test-product",
                    "body_html": "Test description",
                    "variants": [
                        {
                            "price": "19.99",
                            "compare_at_price": "29.99",
                            "available": True
                        }
                    ],
                    "images": [
                        {"src": "https://example.com/image.jpg"}
                    ],
                    "tags": ["test", "product"]
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        self.mock_session.get.return_value = mock_response
        
        products = self.service.get_products()
        
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].title, "Test Product")
        self.assertEqual(products[0].price, "19.99")
        self.assertEqual(products[0].compare_at_price, "29.99")
        self.assertTrue(products[0].available)
        self.assertEqual(products[0].images, ["https://example.com/image.jpg"])
        self.assertEqual(products[0].tags, ["test", "product"])
    
    @patch('app.services.shopify_service.BeautifulSoup')
    def test_get_faqs(self, mock_bs):
        # Mock BeautifulSoup to return FAQ elements
        mock_soup = MagicMock()
        
        # Mock dt/dd elements
        mock_dt = MagicMock()
        mock_dt.get_text.return_value = "Test Question?"
        mock_dd = MagicMock()
        mock_dd.get_text.return_value = "Test Answer"
        
        mock_dt.find_next.return_value = mock_dd
        mock_soup.find_all.return_value = [mock_dt]
        
        mock_bs.return_value = mock_soup
        
        # Mock response for FAQ page
        mock_response = MagicMock()
        mock_response.text = "<html><body><dt>Test Question?</dt><dd>Test Answer</dd></body></html>"
        mock_response.raise_for_status = MagicMock()
        self.mock_session.get.return_value = mock_response
        
        faqs = self.service.get_faqs()
        
        self.assertEqual(len(faqs), 1)
        self.assertEqual(faqs[0].question, "Test Question?")
        self.assertEqual(faqs[0].answer, "Test Answer")


if __name__ == '__main__':
    unittest.main()