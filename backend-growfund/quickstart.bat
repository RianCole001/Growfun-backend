@echo off
echo ========================================
echo GrowFund Backend Quick Start
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
echo Virtual environment created!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate
echo.

echo Step 3: Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed!
echo.

echo Step 4: Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env file created! Please edit it with your settings.
) else (
    echo .env file already exists.
)
echo.

echo Step 5: Running migrations...
python manage.py makemigrations
python manage.py migrate
echo Database setup complete!
echo.

echo Step 6: Creating superuser...
echo Please enter superuser details:
python manage.py createsuperuser
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the server, run:
echo   python manage.py runserver
echo.
echo API will be available at: http://localhost:8000/api/
echo Admin panel at: http://localhost:8000/admin/
echo.
pause
