# House Price Prediction Demo

A Django web application for predicting house prices using machine learning. Features automated model retraining with synthetic data generation and scheduling.

## Features

- **Web Interface**: Simple form to input house features and get price predictions.
- **ML Model**: LinearRegression trained on house price dataset.
- **Synthetic Data Generation**: Adds realistic synthetic rows to expand the dataset.
- **Automated Retraining**: Celery scheduler checks for new data every 10 minutes and retrains if 20+ rows added.
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

### Optional: Enable Automated Retraining (Requires Redis)

1. **Start Redis Server**:
   ```bash
   redis-server
   ```

2. **Start Celery Worker** (in a separate terminal):
   ```bash
   celery -A prediction.celery_app worker --loglevel=info
   ```

3. **Start Celery Beat** (in another terminal):
   ```bash
   celery -A prediction.celery_app beat --loglevel=info
   ```

## Usage

- Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- Fill the prediction form with house details and submit to get estimated price.
- To add synthetic data: `python prediction/append_synthetic.py` (appends 20 rows, cleans negatives).
- The model retrains automatically if new data is detected (when using Celery).

## Technologies

- Django
- scikit-learn
- pandas
- Celery
- Redis
- watchdog