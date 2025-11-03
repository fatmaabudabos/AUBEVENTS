from django.contrib import admin
from django.urls import path, include, re_path
from backend import events_views
from django.http import JsonResponse
from django.views.generic import TemplateView

def root_index(_request):
    """Simple root endpoint to help discover APIs."""
    return JsonResponse({
        "message": "AUBEVENTS API root",
        "auth": "/auth/",
        "admin": "/admin/",
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    # Events API
    path('api/events', events_views.events_create, name='events_create'),
    path('api/events/<int:event_id>', events_views.events_detail, name='events_detail'),
    path('api/events/register', events_views.events_register, name='events_register'),
    path('api/events/unregister', events_views.events_unregister, name='events_unregister'),
    path('api/my/events', events_views.my_events, name='my_events'),

    # Optional API root
    path('api/', root_index, name='api_root'),

    # Catch-all for React frontend
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
