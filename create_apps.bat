@echo off
echo Creation des applications...
mkdir apps
python manage.py startapp pigeons apps/pigeons
python manage.py startapp couples apps/couples
python manage.py startapp reproductions apps/reproductions
python manage.py startapp cages apps/cages
python manage.py startapp sales apps/sales
python manage.py startapp users apps/users
echo Termine!
ls apps/
