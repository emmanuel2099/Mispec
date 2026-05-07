web: gunicorn mispec.wsgi:application --log-file - --timeout 120
worker: celery -A mispec worker --loglevel=info
beat: celery -A mispec beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
geocoding_worker: celery -A mispec worker -Q geocoding_queue --loglevel=info
