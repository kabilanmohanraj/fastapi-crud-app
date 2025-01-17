# Library Management Application - Project Structure Documentation

## Project Overview
A FastAPI-based library management system with user authentication, book management, and event handling capabilities.

## Directory Structure

### Root Directory
- `Procfile`: Heroku deployment configuration
- `requirements.txt`: Python package dependencies for the virtual environment

### Backend Structure (`/backend/app/`)

#### Main Components
- `main.py`: Application entry point
- `config.py`: Application settings
- `models.py`: DB and API data models
- `shared_queue.py`: Queue management for streaming events

#### API Layer (`/backend/app/api/`)
- **Dependencies**: `/api/dependencies.py`
  - Shared API dependencies

- **Routes** (`/api/routes/`):
  - `books.py`: Book management endpoints
  - `events.py`: Event handling endpoints
  - `login.py`: Authentication endpoints
  - `users.py`: User management endpoints

#### Core Components (`/backend/app/core/`)
- `db.py`: Database connection and configuration
- `db_utils.py`: Database utilities
- `security.py`: Authentication utilities

#### Database (`/backend/app/db/`)
- `books.db`: The provided SQLite database file

#### Tests (`/backend/app/tests/`)
Test directory for application unit tests

## Development Setup

1. The application entrypoint is in the `backend/app` directory
2. Dependencies are managed through both Pipenv
3. Tests are organized in the `tests` directory
4. Database file is stored in the `db` directory

## Instructions to run the application on the local system

1. Clone the repository:
```bash
git clone https://github.com/kabilanmohanraj/fastapi-crud-app
cd library-management
```

2. Set up the Python virtual environment using `Pipenv`:
```bash
pipenv install
pipenv shell
```

3. Run the application:
```bash
PYTHONPATH=$(pwd) uvicorn backend.app.main:library_app --host=0.0.0.0 --port=8000 --reload
```

4. Access the application:
   - Main API: http://localhost:8000
   - API Documentation (Swagger UI): http://localhost:8000/docs

5. Testing the API endpoints:
   - Authentication: An admin user is created when the application starts. This use can be used to authenticate and obtain a JWT token to test the other endpoints with added security.
```
Admin username: root@test.com
Admin password: admin
```
