import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from celery import shared_task

logger = logging.getLogger(__name__)

# ML Engine & Orchestration
class HousePricePredictor:
    def __init__(self):
        self.dir_path = os.path.dirname(__file__)
        self.csv_path = os.path.join(self.dir_path, 'house_price_clean.csv')
        self.model_path = os.path.join(self.dir_path, 'ml_model.joblib')
        self.scaler_path = os.path.join(self.dir_path, 'scaler.joblib')
        self.training_state_path = os.path.join(self.dir_path, 'training_state.txt')
        self.last_trained_row_count = self._load_training_state()

    def _load_training_state(self):
        """Load the last trained row count from file."""
        if os.path.exists(self.training_state_path):
            try:
                with open(self.training_state_path, 'r') as f:
                    return int(f.read().strip())
            except (ValueError, IOError):
                return 0
        return 0

    def _save_training_state(self):
        """Save the current trained row count to file."""
        try:
            with open(self.training_state_path, 'w') as f:
                f.write(str(self.last_trained_row_count))
        except IOError:
            logger.warning("Could not save training state")

    def train(self, reason="Scheduled"):
        try:
            if not os.path.exists(self.csv_path):
                logger.warning("CSV file not found, skipping training.")
                return

            df = pd.read_csv(self.csv_path)
            if df.empty or 'price' not in df.columns:
                logger.warning("Invalid CSV data, skipping training.")
                return

            current_row_count = len(df)

            # Training logic
            X = df.drop('price', axis=1)
            y = df['price']

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)

            model = LinearRegression()
            model.fit(X_train_scaled, y_train)

            joblib.dump(model, self.model_path)
            joblib.dump(scaler, self.scaler_path)

            self.last_trained_row_count = current_row_count
            self._save_training_state()
            logger.info(f"--- Model Retrained ({reason}). Total Rows: {current_row_count} ---")
        except Exception as e:
            logger.error(f"Error during training: {e}")

    def check_for_new_data(self):
        """Checks if new rows have been added and retrains if needed."""
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path)
            current_count = len(df)

            logger.info(f"Current row count: {current_count}, Last trained: {self.last_trained_row_count}")

            # Retrain if we have 10 or more new rows (reduced threshold for more responsiveness)
            if current_count >= self.last_trained_row_count + 10:
                logger.info(f"Detected {current_count - self.last_trained_row_count} new rows, retraining model...")
                self.train(reason=f"{current_count - self.last_trained_row_count} New Rows Detected")
            else:
                logger.debug("No significant new data detected")

    def predict(self, features):
        """Predict house price based on input features."""
        try:
            if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
                raise FileNotFoundError("Model or scaler not found. Please train the model first.")

            model = joblib.load(self.model_path)
            scaler = joblib.load(self.scaler_path)

            features_scaled = scaler.transform([features])
            prediction = model.predict(features_scaled)
            return prediction[0]
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return None

# File Watcher (Detects CSV File Changes)
class CSVFileHandler(FileSystemEventHandler):
    def __init__(self, csv_path):
        super().__init__()
        self.csv_path = csv_path

    def on_modified(self, event):
        if event.is_directory: return
        if event.src_path.endswith('house_price_clean.csv'):
            logger.info(f"CSV file modified: {event.src_path}")
            predictor = HousePricePredictor()
            predictor.check_for_new_data()

    def on_created(self, event):
        if event.is_directory: return
        if event.src_path.endswith('house_price_clean.csv'):
            logger.info(f"New CSV detected: {event.src_path}")
            predictor = HousePricePredictor()
            predictor.train(reason="New CSV File Detected")

# Function to start file watcher
def start_csv_watcher():
    """Start watching the CSV file for changes."""
    predictor = HousePricePredictor()
    csv_dir = os.path.dirname(predictor.csv_path)

    event_handler = CSVFileHandler(predictor.csv_path)
    observer = Observer()
    observer.schedule(event_handler, csv_dir, recursive=False)
    observer.start()

    logger.info(f"Started watching CSV file: {predictor.csv_path}")
    return observer


# Celery periodic tasks
@shared_task
def celery_train_model():
    predictor = HousePricePredictor()
    predictor.train(reason="Celery Periodic Task")

@shared_task
def celery_check_for_new_data():
    predictor = HousePricePredictor()
    predictor.check_for_new_data()
