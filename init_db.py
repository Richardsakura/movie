import os
from django.core.management.utils import get_random_secret_key

# Set the secret key
SECRET_KEY = get_random_secret_key()

# Create the necessary tables in the database
import django
from django.db import connection
from django.apps import apps

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation.settings')
django.setup()

# Create models (You can update these models based on your project's needs)
from core.models import User, Movie, Review  # Import your models here

# Run migrations
from django.core.management import call_command
call_command('migrate')  # Apply all migrations

# You can also add some initial data if necessary, e.g. create some default users, movies etc.
# Example: User.objects.create(username='admin', password='admin123')
