from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import jwt

from backend.schemas import EventCreate, EventUpdate
from backend.crud import create_event, get_event, update_event, delete_event_by_id, list_all_events
from database.database import get_user


def _auth_from_request(request: HttpRequest):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None
    email = payload.get("email")
    if not email:
        return None
    return get_user(email)


def _require_admin(request: HttpRequest):
    user = _auth_from_request(request)
    if not user or not getattr(user, "is_admin", False):
        return None
    return user


def _parse_json(request: HttpRequest) -> Dict[str, Any]:
    try:
        body = request.body.decode("utf-8") or "{}"
        return json.loads(body)
    except Exception:
        return {}


def _eventout_to_json(evt) -> Dict[str, Any]:
    if not evt:
        return None
    # Map date -> time for the frontend Admin panel
    return {
        "id": evt.id,
        "title": evt.title,
        "description": getattr(evt, "description", None),
        "time": (getattr(evt, "date", None) or datetime.utcnow()).isoformat(timespec="seconds") if getattr(evt, "date", None) else None,
        "location": getattr(evt, "location", None),
        "capacity": getattr(evt, "capacity", None),
        "organizers": getattr(evt, "organizers", []) or [],
        "speakers": getattr(evt, "speakers", []) or [],
    }


@csrf_exempt
def events_create(request: HttpRequest):
    if request.method == "GET":
        # Public list of events
        items = [
            {
                "id": e.id,
                "title": e.title,
                "description": getattr(e, "description", None),
                "time": (getattr(e, "date", None) or datetime.utcnow()).isoformat(timespec="seconds") if getattr(e, "date", None) else None,
                "location": getattr(e, "location", None),
                "capacity": getattr(e, "capacity", None),
                "organizers": getattr(e, "organizers", []) or [],
                "speakers": getattr(e, "speakers", []) or [],
            }
            for e in list_all_events()
        ]
        return JsonResponse({"events": items})
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    if not _require_admin(request):
        return JsonResponse({"error": "Admin privileges required"}, status=403)

    data = _parse_json(request)
    # Map 'time' -> 'date'
    if "time" in data and data.get("time"):
        try:
            data["date"] = datetime.fromisoformat(str(data["time"]))
        except Exception:
            return JsonResponse({"error": "Invalid time format (expected ISO 8601)"}, status=400)
    try:
        evt_in = EventCreate(
            title=data.get("title"),
            description=data.get("description"),
            date=data.get("date"),
            location=data.get("location"),
            capacity=data.get("capacity"),
            organizers=data.get("organizers"),
            speakers=data.get("speakers"),
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    evt = create_event(evt_in)
    out = _eventout_to_json(get_event(evt.id))
    return JsonResponse({"message": "Event created", **(out or {})}, status=201)


@csrf_exempt
def events_detail(request: HttpRequest, event_id: int):
    method = request.method.upper()

    if method == "GET":
        evt = get_event(event_id)
        if not evt:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse(_eventout_to_json(evt))

    if method == "PATCH":
        if not _require_admin(request):
            return JsonResponse({"error": "Admin privileges required"}, status=403)
        data = _parse_json(request)
        # Map 'time' -> 'date' if present
        if "time" in data and data.get("time"):
            try:
                data["date"] = datetime.fromisoformat(str(data["time"]))
            except Exception:
                return JsonResponse({"error": "Invalid time format (expected ISO 8601)"}, status=400)
        try:
            evt_in = EventUpdate(**{k: v for k, v in data.items() if k in {"title","description","date","location","capacity","organizers","speakers"}})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        updated = update_event(event_id, evt_in)
        if not updated:
            return JsonResponse({"error": "Not found"}, status=404)
        out = _eventout_to_json(updated)
        return JsonResponse({"message": "Event updated", **(out or {})})

    if method == "DELETE":
        if not _require_admin(request):
            return JsonResponse({"error": "Admin privileges required"}, status=403)
        ok = delete_event_by_id(event_id)
        if not ok:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse({"message": "Event deleted"})

    return JsonResponse({"error": "Method not allowed"}, status=405)
