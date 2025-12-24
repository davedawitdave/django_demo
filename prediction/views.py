from django.shortcuts import render
from django.http import JsonResponse
from .models import HousePricePredictor

def home(request):
    """Renders the main input form."""
    return render(request, 'index.html')

def predict(request):
    """Handles the form submission and returns the prediction."""
    if request.method == 'POST':
        try:
            # Extract data from form
            # Note: We must cast these to numbers as the model expects
            features = [
                int(request.POST.get('area')),
                int(request.POST.get('bedrooms')),
                int(request.POST.get('bathrooms')),
                int(request.POST.get('stories')),
                int(request.POST.get('mainroad')),
                int(request.POST.get('guestroom')),
                int(request.POST.get('basement')),
                int(request.POST.get('hotwaterheating')),
                int(request.POST.get('airconditioning')),
                int(request.POST.get('parking')),
                int(request.POST.get('prefarea')),
                int(request.POST.get('furnishingstatus')),
            ]
            
            predictor = HousePricePredictor()
            result = predictor.predict(features)
            
            return render(request, 'index.html', {'prediction': result})
            
        except Exception as e:
            return render(request, 'index.html', {'error': str(e)})

    return render(request, 'index.html')