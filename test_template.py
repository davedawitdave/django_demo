import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.template.loader import get_template

try:
    template = get_template('index.html')
    print("Template found")
    print("Template source length:", len(template.template.source))
except Exception as e:
    print("Error:", e)