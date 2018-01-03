from django.conf.urls import url

from .views import preview_daily_digest

urlpatterns = [
    url(r'^admin/daily-digest-preview/$', preview_daily_digest, name='preview-daily-digest'),
]
