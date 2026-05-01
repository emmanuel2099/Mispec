# Local Development Settings
# This file uses SQLite for local development without needing AWS RDS connection

from .settings import *

# Override database to use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use local Redis or disable Celery for local development
# Comment out if you don't have Redis running locally
try:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
except:
    # If Redis is not available, use in-memory broker
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

print("=" * 80)
print("🔧 USING LOCAL DEVELOPMENT SETTINGS")
print("=" * 80)
print("✓ Database: SQLite (db.sqlite3)")
print("✓ Celery: Local/Disabled")
print("=" * 80)
