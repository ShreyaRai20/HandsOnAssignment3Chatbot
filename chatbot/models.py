"""
models.py

This app does not define any custom Django models of its own. ChatterBot's
SQLStorageAdapter manages its own database tables (statements, tags, etc.)
directly through SQLAlchemy, using the same SQLite file as the rest of the
Django project (see DATABASES / CHATTERBOT['database_uri'] in settings.py).

This file is kept (rather than deleted) because Django's app-loading system
expects every app to have a models module, and future features -- e.g.
storing per-user chat history through Django's own ORM -- could be added
here later.
"""

from django.db import models  # noqa: F401  (kept for potential future models)
