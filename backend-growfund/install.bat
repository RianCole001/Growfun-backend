@echo off
echo Installing GrowFund Backend...
echo.

echo Step 1: Installing dependencies...
py -m pip install Django==4.2.7
py -m pip install djangorestframework==3.14.0
py -m pip install django-cors-headers==4.3.1
py -m pip install djangorestframework-simplejwt==5.3.1
py -m pip install python-decouple==3.8
py -m pip install Pillow==10.1.0

echo.
echo Step 2: Running migrations...
py manage.py makemigrations
py manage.py migrate

echo.
echo Installation complete!
echo.
echo To create admin user, run: py manage.py createsuperuser
echo To start server, run: py manage.py runserver
echo.
pause
