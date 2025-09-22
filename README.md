
# AUBEVENTS

AUBEVENTS is a web application for event registration and management at AUB. This project includes a robust backend for user authentication and password management, and is ready for frontend integration.

## Features
- User signup and email verification
- Secure login with password hashing (bcrypt)
- Password reset flow (request, email code, confirm new password)
- Password strength enforcement
- Rate limiting for password reset requests
- Comprehensive error handling
- Unit tests for all authentication and password endpoints

## Folder Structure
```
AUBEVENTS/
  backend/        # Django project settings and URLs
  accounts/       # Authentication and password management app
  database/       # SQLModel-based user and token management
  frontend/       # (Placeholder) React/Next.js web UI
  infra/          # DevOps, environment, and deployment scripts
  docs/           # Documentation and diagrams
  manage.py       # Django management script
  README.md       # Project documentation
```

## Backend Setup
1. **Install dependencies:**
	- Python 3.10+
	- Django, djangorestframework, bcrypt, sqlmodel, PyJWT, django-cors-headers
	- Install with: `pip install -r requirements.txt`
2. **Database setup:**
	- Run: `python -m AUBEVENTS.database.createDatabase`
3. **Run tests:**
	- `python manage.py test accounts`
4. **Start the server:**
	- `python manage.py runserver`

## API Endpoints (accounts)
- `POST /auth/signup/` — Register a new user
- `POST /auth/verify/` — Verify email
- `POST /auth/login/` — Login
- `POST /auth/password-reset-request/` — Request password reset code
- `POST /auth/password-reset-confirm/` — Confirm new password

## Frontend (Placeholder)
- The `frontend/` folder is ready for a React/Next.js app.
- To get started: `npx create-next-app@latest .` inside the `frontend/` folder.
- Connect the frontend to the backend API endpoints for signup and login.

## CORS
- Make sure to configure CORS in Django to allow frontend requests (see `django-cors-headers`).


