# House Price Prediction Demo

A Django web application for predicting house prices using machine learning. Features automated model retraining with synthetic data generation and scheduling.

## Features

- **Web Interface**: Simple form to input house features and get price predictions.
- **ML Model**: LinearRegression trained on house price dataset.
- **Synthetic Data Generation**: Adds realistic synthetic rows to expand the dataset.
- **Automated Retraining**: Real-time file watcher + Celery scheduler checks for new data every 2 minutes and retrains if 10+ rows added.
- **Data Cleaning**: Automatically removes rows with negative values.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Train Initial Model**:
   ```bash
   python manage.py shell -c "from prediction.ml_service import HousePricePredictor; p=HousePricePredictor(); p.train()"
   ```

4. **Run Server**:
   ```bash
   python manage.py runserver
   ```



## Usage

- Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser*(or your choosen port).
- Fill the prediction form with house details and submit to get estimated price.
- To add synthetic data: `python prediction/append_synthetic.py` (appends 20 rows, cleans negatives).
- **Automatic Retraining**: Model retrains automatically when 10+ new rows are added to the CSV (works immediately with Django server, or every 2 minutes with Celery).

## Technologies

- Django
- scikit-learn
- pandas
- Celery
- Redis
- watchdogs