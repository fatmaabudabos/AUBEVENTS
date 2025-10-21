# Student Signup → Student Dashboard Flow

This document summarizes the backend and frontend changes enabling AUB students to see the student interface immediately after signup and verification.

## What’s implemented

- Auto-login after successful email verification and immediate redirect:
  - Admins → `/admin`
  - Students → `/dashboard`
- Student Dashboard at `/dashboard`:
  - Lists events from backend (`GET /api/events`)
  - Search by title/location/description
  - Shows registration state per event
  - Register / Unregister to events (requires login)
- Backend endpoints (Django):
  - `GET  /api/events`               → public list of events
  - `GET  /api/events/<id>`          → event details
  - `POST /api/events`               → create (admin only)
  - `PATCH/DELETE /api/events/<id>`  → edit/delete (admin only)
  - `POST /api/events/register`      → register current user to an event
  - `POST /api/events/unregister`    → unregister current user from an event
  - `GET  /api/my/events`            → list current user’s registered events

Auth helper used: `GET /auth/me/` returns `{ email, is_verified, is_admin }`.

## Files touched

- Backend
  - `backend/events_views.py` → Added `events_register`, `events_unregister`, `my_events`
  - `backend/urls.py`         → Wired new endpoints
- Frontend
  - `frontend/src/Signup.jsx`     → Auto-login after verification and role-based redirect
  - `frontend/src/Dashboard.jsx`  → Full student dashboard (list/search/register/unregister)

## Manual test plan

1) Backend
- Start: `python manage.py runserver`
- Sanity: `python manage.py check` should pass.

2) Frontend
- Start dev: from `frontend/` run `npm install` then `npm run dev`.
- In browser:
  - Sign up with an AUB email (e.g., `user@mail.aub.edu`).
  - Verify using emailed code (dev hint may show on UI).
  - After verification → should auto-login and redirect:
    - If `is_admin` false → `/dashboard` (student view)
    - If `is_admin` true  → `/admin` (admin panel)
  - On `/dashboard`:
    - See events, search, and register/unregister (logged in).

## Notes
- Allowed email domains are enforced server-side: `aub.edu.lb` and `mail.aub.edu`.
- Role is determined by `is_admin` on the user record; students are non-admins by default.
- Frontend relies on `VITE_API_BASE_URL` (default `http://localhost:8000`).