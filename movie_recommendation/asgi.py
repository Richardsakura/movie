"""
ASGI config for movie_recommendation project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation.settings')

application = get_asgi_application()