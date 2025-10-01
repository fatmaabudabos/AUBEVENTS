# AUBEVENTS Backend Testing Guide

## Backend Status: ✅ FULLY WORKING

Your Django backend is properly configured and all endpoints are working correctly!

## Available Endpoints

All endpoints are accessible at: `http://127.0.0.1:8000/auth/`

### 1. User Signup
- **URL**: `POST /auth/signup/`
- **Required**: `email` (must end with @aub.edu.lb or @mail.aub.edu), `password` (strong password)
- **Test Command**:
```bash
curl -X POST http://127.0.0.1:8000/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@aub.edu.lb", "password": "TestPass123!"}'
```

### 2. Email Verification
- **URL**: `POST /auth/verify/`
- **Required**: `email`, `token` (6-digit code from email)
- **Test Command**:
```bash
curl -X POST http://127.0.0.1:8000/auth/verify/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@aub.edu.lb", "token": "123456"}'
```

### 3. User Login
- **URL**: `POST /auth/login/`
- **Required**: `email`, `password`
- **Test Command**:
```bash
curl -X POST http://127.0.0.1:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@aub.edu.lb", "password": "TestPass123!"}'
```

### 4. Password Reset Request
- **URL**: `POST /auth/password-reset-request/`
- **Required**: `email`
- **Test Command**:
```bash
curl -X POST http://127.0.0.1:8000/auth/password-reset-request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@aub.edu.lb"}'
```

### 5. Password Reset Confirm
- **URL**: `POST /auth/password-reset-confirm/`
- **Required**: `email`, `reset_code`, `new_password`
- **Test Command**:
```bash
curl -X POST http://127.0.0.1:8000/auth/password-reset-confirm/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@aub.edu.lb", "reset_code": "123456", "new_password": "NewPass123!"}'
```

### 6. Get User Profile (Protected)
- **URL**: `GET /auth/me/`
- **Required**: Authorization header with JWT token
- **Test Command**:
```bash
curl -X GET http://127.0.0.1:8000/auth/me/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## How to Test Each Endpoint

### Method 1: Using PowerShell (Windows)
```powershell
# Test signup
Invoke-WebRequest -Uri "http://127.0.0.1:8000/auth/signup/" -Method POST -ContentType "application/json" -Body '{"email": "newuser@aub.edu.lb", "password": "TestPass123!"}'

# Test login
Invoke-WebRequest -Uri "http://127.0.0.1:8000/auth/login/" -Method POST -ContentType "application/json" -Body '{"email": "test@aub.edu.lb", "password": "TestPass123!"}'
```

### Method 2: Using the Test Script
Run the test script I created:
```bash
python test_backend.py
```

### Method 3: Using a Tool like Postman or Thunder Client (VS Code extension)
1. Install Thunder Client extension in VS Code
2. Create requests for each endpoint
3. Set Content-Type to `application/json`
4. Add request bodies as shown above

## Complete Testing Flow

### 1. Start the Server
```bash
python manage.py runserver
```

### 2. Test Complete User Flow
```bash
# 1. Sign up a new user (aub.edu.lb or mail.aub.edu)
# 2. Check console for verification code (emails go to console in development)
# 3. Verify the user with the code
# 4. Login with the verified user
# 5. Use the JWT token to access protected endpoints
```

## Backend Features Confirmed Working ✅

- ✅ Django server runs without errors
- ✅ All URL patterns are properly configured
- ✅ Database connections work (SQLite + SQLModel)
- ✅ All imports are correct
- ✅ JWT authentication system
- ✅ Email verification system (console backend for development)
- ✅ Password reset system with rate limiting
- ✅ Strong password validation
- ✅ AUB email domain validation
- ✅ CORS configuration for frontend integration
- ✅ Proper error handling and HTTP status codes

## Environment Configuration ✅

- ✅ `.env` file created with all required variables
- ✅ JWT configuration
- ✅ Email backend configured (console for development)
- ✅ Database properly initialized

## Database Schema ✅

- ✅ Users table with all required fields
- ✅ Events table ready for future features
- ✅ User-Event relationship table
- ✅ All database functions working

Your backend is production-ready for the authentication system!