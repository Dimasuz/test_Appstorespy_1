#!/bin/sh

celery --app=test_appstorespy_1 worker --loglevel=DEBUG --concurrency=2 -E --logfile=logs/celery.log

#redis-server

exec "$@"