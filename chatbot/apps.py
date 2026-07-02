"""
apps.py

Standard Django AppConfig for the "chatbot" app. This registers the app
with Django so that its management commands (chatbot/management/commands/
chat.py) are discovered and made available via `python manage.py chat`.
"""

from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot"
