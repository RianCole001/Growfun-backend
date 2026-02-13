# Back4app Deployment Guide

## Prerequisites
- Back4app account
- Docker installed locally (for testing)
- Git repository pushed to GitHub

## Step 1: Prepare Environment Variables

Create a `.env` file in the root of your project with production values:

```env
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.back4app.io,localhost
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@growfund.com
FRONTEND_URL=https://your-frontend-url.com
COINGECKO_API_KEY=your-coingecko-api-key
```

## Step 2: Connect to Back4app

1. Go to [Back4app.com](https://www.back4app.com)
2. Create a new app or select existing one
3. Go to **Deploy** section
4. Choose **Docker** as deployment method
5. Connect your GitHub repository

## Step 3: Configure Back4app Settings

1. In Back4app dashboard, go to **Settings**
2. Add environment variables from your `.env` file
3. Set up PostgreSQL database (Back4app provides this)
4. Configure domain/custom URL

## Step 4: Deploy

Back4app will automatically:
1. Build the Docker image
2. Run migrations
3. Collect static files
4. Start the application

## Step 5: Run Migrations on Deployment

After first deployment, run migrations:

```bash
# In Back4app console or via SSH
python manage.py migrate
python manage.py createsuperuser
```

## Testing Locally with Docker

```bash
# Build image
docker build -t growfund-backend .

# Run container
docker run -p 8000:8000 \
  -e SECRET_KEY=test-key \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  growfund-backend
```

## Troubleshooting

### Static files not loading
- Ensure `STATIC_ROOT` is set correctly
- Run `python manage.py collectstatic`

### Database connection errors
- Verify `DB_HOST`, `DB_USER`, `DB_PASSWORD` in environment variables
- Check PostgreSQL is running

### Port issues
- Back4app uses port 8000 by default
- Dockerfile exposes port 8000

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure email settings
- [ ] Set `CORS_ALLOWED_ORIGINS` to your frontend URL
- [ ] Run migrations
- [ ] Create superuser
- [ ] Test API endpoints
- [ ] Monitor logs in Back4app dashboard
