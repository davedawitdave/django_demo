from django.shortcuts import render, redirect
from django.http import JsonResponse
from .ml_service import HousePricePredictor

def home(request):
    """Renders the main input form."""
    predictor = HousePricePredictor()
    context = {
        'last_trained_row_count': predictor.last_trained_row_count
    }
    return render(request, 'index.html', context)

def predict(request):
    """Handles the form submission and returns the prediction."""
    predictor = HousePricePredictor()
    context = {
        'last_trained_row_count': predictor.last_trained_row_count
    }
    
    if request.method == 'POST':
        try:
            # Validate all required fields
            required_fields = [
                'area', 'bedrooms', 'bathrooms', 'stories', 'mainroad',
                'guestroom', 'basement', 'hotwaterheating', 'airconditioning',
                'parking', 'prefarea', 'furnishingstatus'
            ]
            
            # Check if all required fields are present
            if not all(field in request.POST for field in required_fields):
                raise ValueError("Missing required form fields")
            
            # Extract and validate numeric fields
            try:
                features = [
                    float(request.POST.get('area')),
                    float(request.POST.get('bedrooms')),
                    float(request.POST.get('bathrooms')),
                    float(request.POST.get('stories')),
                    int(request.POST.get('mainroad')),
                    int(request.POST.get('guestroom')),
                    int(request.POST.get('basement')),
                    int(request.POST.get('hotwaterheating')),
                    int(request.POST.get('airconditioning')),
                    int(request.POST.get('parking')),
                    int(request.POST.get('prefarea')),
                    int(request.POST.get('furnishingstatus')),
                ]
            except (TypeError, ValueError) as e:
                raise ValueError("Invalid input values. Please check your entries.")
            
            # Make prediction
            result = predictor.predict(features)
            context['prediction'] = result
            
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'index.html', context)