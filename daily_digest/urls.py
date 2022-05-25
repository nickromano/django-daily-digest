try:
    from django.conf.urls import url as re_path
except ImportError:
    from django.urls import re_path

from .views import preview_daily_digest

urlpatterns = [
    re_path(
        r"admin/daily-digest-preview/$",
        preview_daily_digest,
        name="preview-daily-digest",
    ),
]
