web: gunicorn app:app -b 0.0.0.0:$PORT -w 1
celery_datasets: celeryd -A larva_service.celery -l info -E -B -c 1 -Q datasets,default
celery_runs: celeryd -A larva_service.celery -l info -E -c 1 -Q runs
