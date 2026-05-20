from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path


def serve_spa(request):
    index_file = settings.FRONTEND_DIST_DIR / 'index.html'
    if index_file.exists():
        return HttpResponse(index_file.read_text(), content_type='text/html')
    return HttpResponse('Frontend not built. Run npm run build.', status=501)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/properties/', include('properties.urls')),
    path('api/bookings/', include('bookings.urls')),
    re_path(r'^(?!api/|admin/|static/).*$', serve_spa),
]
