from __future__ import annotations

import json
import mimetypes
import os
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone

import jwt

from backend.schemas import EventCreate, EventUpdate, UserEventAction
from backend.crud import (
    create_event,
    get_event,
    update_event,
    delete_event_by_id,
    list_all_events,
    register_user,
    unregister_user,
    list_user_events,
)
from database.database import get_user
from backend.supabase_client import get_supabase_client
from storage3.types import CreateOrUpdateBucketOptions


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


def _emails_match(a: str | None, b: str | None) -> bool:
    """Return True if two emails should be treated as the same admin.

    - Case-insensitive.
    """
    if not a or not b:
        return False
    a = a.strip().lower()
    b = b.strip().lower()
    return a == b


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
        "available_seats": getattr(evt, "available_seats", None),
        "organizers": getattr(evt, "organizers", []) or [],
        "speakers": getattr(evt, "speakers", []) or [],
        "category": getattr(evt, "category", None),
        "image_url": getattr(evt, "image_url", None),
    }


@csrf_exempt
def events_create(request: HttpRequest):
    if request.method == "GET":
        # Check if user is an admin - if so, show only their events
        user = _auth_from_request(request)
        if user and getattr(user, "is_admin", False):
            # Admin user - show only events created by this admin
            q = request.GET.get('q') or request.GET.get('search') or None
            
            # Get raw database rows and filter by created_by before converting to EventOut
            from backend.crud import db_list_events
            raw_events = db_list_events(q)
            
            # Filter events by creator
            filtered_events = [
                e for e in raw_events 
                if _emails_match(getattr(e, "created_by", None), user.email)
            ]
            
            # Convert filtered events to JSON response format
            items = [
                {
                    "id": e.id,
                    "title": e.title,
                    "description": getattr(e, "description", None),
                    "time": (getattr(e, "date", None) or datetime.utcnow()).isoformat(timespec="seconds") if getattr(e, "date", None) else None,
                    "location": getattr(e, "location", None),
                    "capacity": getattr(e, "capacity", None),
                    "available_seats": getattr(e, "available_seats", None),
                    "organizers": getattr(e, "organizers", []) or [],
                    "speakers": getattr(e, "speakers", []) or [],
                    "category": getattr(e, "category", None),
                    "image_url": getattr(e, "image_url", None),
                }
                for e in filtered_events
            ]
            return JsonResponse({"events": items})
        else:
            # Public list of events (for regular users and non-authenticated)
            # Support optional search query param 'q' to filter by title/location/description
            q = request.GET.get('q') or request.GET.get('search') or None
            items = [
                {
                    "id": e.id,
                    "title": e.title,
                    "description": getattr(e, "description", None),
                    "time": (getattr(e, "date", None) or datetime.utcnow()).isoformat(timespec="seconds") if getattr(e, "date", None) else None,
                    "location": getattr(e, "location", None),
                    "capacity": getattr(e, "capacity", None),
                    "available_seats": getattr(e, "available_seats", None),
                    "organizers": getattr(e, "organizers", []) or [],
                    "speakers": getattr(e, "speakers", []) or [],
                    "category": getattr(e, "category", None),
                    "image_url": getattr(e, "image_url", None),
                }
                for e in list_all_events(q)
            ]
            return JsonResponse({"events": items})
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    admin_user = _require_admin(request)
    if not admin_user:
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
            category=data.get("category"),
            image_url=data.get("image_url"),
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    if not getattr(evt_in, "image_url", None):
        return JsonResponse({"error": "Event image is required"}, status=400)

    evt = create_event(evt_in, created_by=admin_user.email)
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
        admin_user = _require_admin(request)
        if not admin_user:
            return JsonResponse({"error": "Admin privileges required"}, status=403)
        
        # Check if the admin is the creator of this event
        evt = get_event(event_id)
        if not evt:
            return JsonResponse({"error": "Not found"}, status=404)
        
        # Get the event from database to check created_by field
        from database.database import get_engine
        from sqlmodel import Session, select
        from database.tables import Events
        
        with Session(get_engine()) as session:
            db_event = session.get(Events, event_id)
            if not db_event:
                return JsonResponse({"error": "Not found"}, status=404)
            if not _emails_match(db_event.created_by, admin_user.email):
                return JsonResponse({"error": "You can only edit events you created"}, status=403)
        
        data = _parse_json(request)
        # Map 'time' -> 'date' if present
        if "time" in data and data.get("time"):
            try:
                data["date"] = datetime.fromisoformat(str(data["time"]))
            except Exception:
                return JsonResponse({"error": "Invalid time format (expected ISO 8601)"}, status=400)
        if "image_url" in data and not (isinstance(data["image_url"], str) and data["image_url"].strip()):
            return JsonResponse({"error": "Event image is required"}, status=400)
        try:
            evt_in = EventUpdate(**{k: v for k, v in data.items() if k in {"title","description","date","location","capacity","organizers","speakers","category","image_url"}})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        updated = update_event(event_id, evt_in)
        if not updated:
            return JsonResponse({"error": "Not found"}, status=404)
        out = _eventout_to_json(updated)
        return JsonResponse({"message": "Event updated", **(out or {})})

    if method == "DELETE":
        admin_user = _require_admin(request)
        if not admin_user:
            return JsonResponse({"error": "Admin privileges required"}, status=403)
        
        # Check if the admin is the creator of this event
        from database.database import get_engine
        from sqlmodel import Session, select
        from database.tables import Events
        
        with Session(get_engine()) as session:
            db_event = session.get(Events, event_id)
            if not db_event:
                return JsonResponse({"error": "Not found"}, status=404)
            if not _emails_match(db_event.created_by, admin_user.email):
                return JsonResponse({"error": "You can only delete events you created"}, status=403)
        
        ok = delete_event_by_id(event_id)
        if not ok:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse({"message": "Event deleted"})

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def events_upload_image(request: HttpRequest):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    admin_user = _require_admin(request)
    if not admin_user:
        return JsonResponse({"error": "Admin privileges required"}, status=403)

    client = get_supabase_client()
    if client is None:
        return JsonResponse({"error": "Supabase storage is not configured."}, status=503)

    uploaded = request.FILES.get("image")
    if not uploaded:
        return JsonResponse({"error": "Missing file field 'image'."}, status=400)

    allowed_ext = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    _, ext = os.path.splitext(uploaded.name or "upload")
    ext = ext.lower()
    if ext not in allowed_ext:
        guessed_ext = mimetypes.guess_extension(uploaded.content_type or "")
        if guessed_ext in allowed_ext:
            ext = guessed_ext
        else:
            return JsonResponse({"error": "Unsupported file type."}, status=400)

    if uploaded.size and uploaded.size > 8 * 1024 * 1024:
        return JsonResponse({"error": "Image exceeds 8 MB limit."}, status=400)

    bucket = getattr(settings, "SUPABASE_BUCKET", "event-images")
    storage_client = client.storage
    try:
        existing_buckets = {bucket_info.name for bucket_info in storage_client.list_buckets()}
    except Exception as exc:
        return JsonResponse({"error": f"Failed to list Supabase buckets: {exc}"}, status=500)

    if bucket not in existing_buckets:
        try:
            options = CreateOrUpdateBucketOptions(public=getattr(settings, "SUPABASE_BUCKET_PUBLIC", True))
            storage_client.create_bucket(bucket, options=options)
        except Exception as exc:
            return JsonResponse({"error": f"Failed to create Supabase bucket '{bucket}': {exc}"}, status=500)

    storage = storage_client.from_(bucket)

    timestamp = timezone.now()
    object_path = f"events/{timestamp:%Y/%m/%d}/{uuid4().hex}{ext}"
    content_type = uploaded.content_type or mimetypes.guess_type(uploaded.name or "")[0] or "application/octet-stream"

    try:
        upload_response = storage.upload(
            object_path,
            uploaded.read(),
            {"contentType": content_type}
        )
    except Exception as exc:
        return JsonResponse({"error": f"Supabase upload failed: {exc}"}, status=400)

    error = getattr(upload_response, "error", None)
    if error:
        return JsonResponse({"error": str(error)}, status=500)

    public_response = storage.get_public_url(object_path)
    public_url = None
    if isinstance(public_response, dict):
        public_url = public_response.get("publicUrl") or public_response.get("public_url")
        if not public_url and isinstance(public_response.get("data"), dict):
            public_url = public_response["data"].get("publicUrl")
    elif hasattr(public_response, "data"):
        data_attr = public_response.data
        if isinstance(data_attr, dict):
            public_url = data_attr.get("publicUrl")
        else:
            public_url = data_attr

    if not public_url:
        # Fallback to manual construction (bucket must be public)
        base_url = getattr(settings, "SUPABASE_URL", "").rstrip("/")
        public_url = f"{base_url}/storage/v1/object/public/{bucket}/{object_path}" if base_url else object_path

    return JsonResponse({
        "image_url": public_url,
        "path": object_path,
        "content_type": content_type,
    }, status=201)


@csrf_exempt
def events_register(request: HttpRequest):
    """Register the current authenticated user to an event.

    POST body: { "event_id": number }
    Requires Authorization: Bearer <jwt>
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user = _auth_from_request(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    data = _parse_json(request)
    event_id = data.get("event_id")
    try:
        event_id = int(event_id)
    except Exception:
        return JsonResponse({"error": "event_id must be an integer"}, status=400)
    action = UserEventAction(email=user.email, event_id=event_id)
    res = register_user(action)
    # Map failure reasons to appropriate HTTP statuses (defense-in-depth)
    if res.success:
        return JsonResponse({"message": res.message, "success": True}, status=200)
    reason = getattr(res, "reason", None)
    if reason == 'full' or reason == 'already_registered':
        status_code = 409
    elif reason == 'not_found':
        status_code = 404
    else:
        status_code = 400
    return JsonResponse({"message": res.message, "success": False, "reason": reason}, status=status_code)


@csrf_exempt
def events_unregister(request: HttpRequest):
    """Unregister the current authenticated user from an event.

    POST body: { "event_id": number }
    Requires Authorization: Bearer <jwt>
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user = _auth_from_request(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    data = _parse_json(request)
    event_id = data.get("event_id")
    try:
        event_id = int(event_id)
    except Exception:
        return JsonResponse({"error": "event_id must be an integer"}, status=400)
    action = UserEventAction(email=user.email, event_id=event_id)
    res = unregister_user(action)
    status_code = 200 if res.success else 400
    return JsonResponse({"message": res.message, "success": res.success}, status=status_code)


@csrf_exempt
def my_events(request: HttpRequest):
    """List events that the current authenticated user is registered for."""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user = _auth_from_request(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    q = request.GET.get('q') or request.GET.get('search') or None
    items = [
        {
            "id": e.id,
            "title": e.title,
            "description": getattr(e, "description", None),
            "time": (getattr(e, "date", None) or datetime.utcnow()).isoformat(timespec="seconds") if getattr(e, "date", None) else None,
            "location": getattr(e, "location", None),
            "capacity": getattr(e, "capacity", None),
            "available_seats": getattr(e, "available_seats", None),
            "organizers": getattr(e, "organizers", []) or [],
            "speakers": getattr(e, "speakers", []) or [],
            "category": getattr(e, "category", None),
            "image_url": getattr(e, "image_url", None),
        }
        for e in list_user_events(user.email, q)
    ]
    return JsonResponse({"events": items})
