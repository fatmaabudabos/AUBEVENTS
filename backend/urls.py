from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def root_index(_request):
    """Simple root endpoint to help discover APIs."""
    return JsonResponse({
        "message": "AUBEVENTS API root",
        "auth": "/auth/",
        "admin": "/admin/",
    })

urlpatterns = [
    path('', root_index, name='api_root'),
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
]
