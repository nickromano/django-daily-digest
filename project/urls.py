try:
    from django.conf.urls import url as re_path
    from django.conf.urls import include
except ImportError:
    from django.urls import re_path, include

from django.contrib import admin


urlpatterns = [
    re_path(r"^", include("daily_digest.urls")),
    re_path(r"^admin/", admin.site.urls),
]
