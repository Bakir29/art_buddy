@echo off

echo Setting up Art Buddy backend development environment...

REM Copy environment file if it doesn't exist
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
    echo Please update the .env file with your settings
)

REM Start services
echo Starting Docker services...
docker-compose up -d postgres

echo Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak >nul

REM Run migrations
echo Running database migrations...
docker-compose run --rm backend alembic upgrade head

echo Starting all services...
docker-compose up -d

echo Development environment is ready!
echo API will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/docs
echo n8n will be available at: http://localhost:5678
echo n8n login: admin / password

pause