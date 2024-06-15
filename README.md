docker-compose build
docker-compose up -d
docker-compose run backend python mange.py makemigrations
docker-compose run backend python mange.py migrate
docker-compose exec db psql --username=adrift
docker-compose run backend python manage.py createsuperuser