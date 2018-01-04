# -*- coding: utf-8 -*-
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .config import daily_digest_config
from .utils import charts_data_for_config


@staff_member_required
def preview_daily_digest(request):
    context = {
        'title': daily_digest_config.title,
        'charts': charts_data_for_config()
    }
    return render(request, 'daily_digest/email.html', context)
