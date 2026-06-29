"""
Main URL file for jobportal project.
All URLs are handled by the jobs app.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),          # Django built-in admin
    path('', include('jobs.urls')),            # All our app URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# The last line makes uploaded files (resumes) accessible via browser
