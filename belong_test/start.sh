JOB_SERVER='127.0.0.1:8000'
python manage.py makemigrations
python manage.py runserver $JOB_SERVER  &
python manage.py start_processing --job_server="http://$JOB_SERVER" --workers=4 &

python -m worker_app.tests $JOB_SERVER
