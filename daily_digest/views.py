# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .config import daily_digest_config
from .utils import charts_data_for_config


@login_required
def preview_daily_digest(request):
    if not request.user.is_staff:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    context = {
        'title': daily_digest_config.title,
        'charts': charts_data_for_config()
    }
    return render(request, 'daily_digest/email.html', context)
