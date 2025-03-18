bind = "0.0.0.0:8000"  # or your desired port
workers = 4  # Adjust as needed
worker_class = "gunicorn.workers.sync.SyncWorker"
wsgi_app = "app:app"  # Replace your_app_name with your file's name