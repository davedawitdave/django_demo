from django.test import TestCase, Client
from django.urls import reverse
import os
from .models import HousePricePredictor

class PredictionTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status(self):
        """Test if the home page loads successfully."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_prediction_logic_exists(self):
        """Test if the predictor class can be instantiated."""
        predictor = HousePricePredictor()
        self.assertIsNotNone(predictor)
        
    def test_csv_existence(self):
        """Ensure the source CSV is present for training."""
        predictor = HousePricePredictor()
        self.assertTrue(os.path.exists(predictor.csv_path), "CSV file is missing!")