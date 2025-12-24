import os
import joblib
import pandas as pd
import numpy as np
from django.db import models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from apscheduler.schedulers.background import BackgroundScheduler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 1. Database Model
class HousePrice(models.Model):
    price = models.BigIntegerField()
    area = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    stories = models.IntegerField()
    mainroad = models.IntegerField()
    guestroom = models.IntegerField()
    basement = models.IntegerField()
    hotwaterheating = models.IntegerField()
    airconditioning = models.IntegerField()
    parking = models.IntegerField()
    prefarea = models.IntegerField()
    furnishingstatus = models.IntegerField()

# 2. ML Engine & Orchestration
class HousePricePredictor:
    def __init__(self):
        self.dir_path = os.path.dirname(__file__)
        self.csv_path = os.path.join(self.dir_path, 'house_price_clean.csv')
        self.model_path = os.path.join(self.dir_path, 'ml_model.joblib')
        self.scaler_path = os.path.join(self.dir_path, 'scaler.joblib')
        self.last_trained_row_count = 0 

    def train(self, reason="Scheduled"):
        if not os.path.exists(self.csv_path):
            return
        
        df = pd.read_csv(self.csv_path)
        current_row_count = len(df)
        
        # Training logic
        X = df.drop('price', axis=1)
        y = df['price']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        joblib.dump(model, self.model_path)
        joblib.dump(scaler, self.scaler_path)
        
        self.last_trained_row_count = current_row_count
        print(f"--- Model Retrained ({reason}). Total Rows: {current_row_count} ---")

    def check_for_new_data(self):
        """Checks if 20 or more new rows have been added."""
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path)
            if len(df) >= self.last_trained_row_count + 20:
                self.train(reason="20 New Rows Detected")

    def predict(self, features):
        """Predict house price based on input features."""
        if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
            raise FileNotFoundError("Model or scaler not found. Please train the model first.")
        
        model = joblib.load(self.model_path)
        scaler = joblib.load(self.scaler_path)
        
        features_scaled = scaler.transform([features])
        prediction = model.predict(features_scaled)
        return prediction[0]

# 3. File Watcher (Detects New CSV Files)
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        if event.src_path.endswith('.csv'):
            print(f"New CSV detected: {event.src_path}")
            predictor = HousePricePredictor()
            predictor.train(reason="New File Detected")

def start_orchestration():
    predictor = HousePricePredictor()
    scheduler = BackgroundScheduler()
    
    # Trigger 1: Every 4 hours
    scheduler.add_job(predictor.train, 'interval', hours=4)
    
    # Trigger 2: Check row count every 10 minutes
    scheduler.add_job(predictor.check_for_new_data, 'interval', minutes=1)
    
    scheduler.start()

    # Trigger 3: File System Watcher for new files
    observer = Observer()
    observer.schedule(NewFileHandler(), path=os.path.dirname(__file__), recursive=False)
    observer.start()