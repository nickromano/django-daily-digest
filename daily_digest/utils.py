# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

import leather
import pytz
from cairosvg import svg2png
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.utils.text import slugify
from email.mime.image import MIMEImage
from django.template.loader import get_template

los_angeles_timezone = pytz.timezone('America/Los_Angeles')

leather.theme.background_color = '#ffffff'
leather.theme.title_font_family = 'Helvetica'
leather.theme.legend_font_family = 'Helvetica'
leather.theme.tick_font_family = 'Helvetica'
PRIMARY_STROKE_COLOR = '#4383CC'
PREV_PERIOD_STROKE_COLOR = '#B4CDEB'

EMAIL_TIME_PERIOD = 7


def series_labels(series_1_count, series_2_count):
    if series_2_count > 0:
        percent_change = int(round((float(series_1_count - series_2_count) / series_2_count) * 100, 0))
        if percent_change > 0:
            percent_change = '+{}%'.format(percent_change)
        else:
            percent_change = '{}%'.format(percent_change)
    else:
        percent_change = ''

    current_label = 'Last {} Days ({}) {}'.format(EMAIL_TIME_PERIOD, series_1_count, percent_change)
    prev_period_label = 'Previous Period ({})'.format(series_2_count)
    return current_label, prev_period_label


def series_data_for_model(start_query, field, prev_period=False, exclude_today=False):
    start_of_today = datetime.utcnow().replace(hour=0, minute=0, second=0).replace(tzinfo=los_angeles_timezone)
    start_of_today = start_of_today.astimezone(pytz.UTC)

    if exclude_today:
        start_of_today = start_of_today - timedelta(days=1)

    if prev_period:
        period_end = start_of_today - timedelta(days=EMAIL_TIME_PERIOD)
        period_start = period_end - timedelta(days=EMAIL_TIME_PERIOD)
    else:
        period_end = start_of_today + timedelta(days=1)  # End of today
        period_start = period_end - timedelta(days=EMAIL_TIME_PERIOD + 1)

    filters = {
        '{}__gte'.format(field): period_start,
        '{}__lt'.format(field): period_end
    }
    series_data = start_query.filter(**filters).order_by(field).values_list(
        field, flat=True
    )
    series_data = list(map(
        lambda x: x.astimezone(los_angeles_timezone).date(),
        series_data
    ))

    grouped_by_date = []
    for i in range(1, EMAIL_TIME_PERIOD + 1):
        day = (period_start + timedelta(days=i)).date()
        count = 0
        for user_date in series_data:
            if user_date == day:
                count += 1
        if prev_period:
            day = day + timedelta(days=EMAIL_TIME_PERIOD)  # offset date to show both series on one chart
        grouped_by_date.append([day, count])

    return grouped_by_date, len(series_data)


def svg_data_for_query(start_query, field, chart_name, exclude_today=False):
    data, total_count = series_data_for_model(
        start_query, field, exclude_today=exclude_today)
    data_prev_period, total_count_prev_period = series_data_for_model(
        start_query, field, prev_period=True, exclude_today=exclude_today)

    # Show every date on the x axis
    x_axis_ticks = []
    for item in data:
        x_axis_ticks.append(item[0])

    chart = leather.Chart()
    chart.add_x_axis(ticks=x_axis_ticks)
    current_label, prev_period_label = series_labels(total_count, total_count_prev_period)
    chart.add_line(data, name=current_label, stroke_color=PRIMARY_STROKE_COLOR)
    chart.add_line(data_prev_period, name=prev_period_label, stroke_color=PREV_PERIOD_STROKE_COLOR, stroke_dasharray='5')
    chart.to_svg('/tmp/{}.svg'.format(chart_name), width=480, height=240)

    with open('/tmp/{}.svg'.format(chart_name)) as svgfile:
        svg_data = svgfile.read()
    svg2png(url='/tmp/{}.svg'.format(chart_name), write_to='/tmp/{}.png'.format(chart_name), scale=2)

    return svg_data


def charts_data_for_config(chart_format='svg'):
    charts_data = []
    config = getattr(settings, 'DAILY_DIGEST_CONFIG', {})
    charts = config.get('charts', [])
    for chart in charts:
        title = chart['title']
        app_label = chart['app_label']
        model = chart['model']
        date_field = chart['date_field']
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        filter_kwargs = chart.get('filter_kwargs', {})
        queryset = content_type.model_class().objects.filter(**filter_kwargs)
        result = {
            'title': title,
            'svg_data': svg_data_for_query(
                queryset, date_field, slugify(title),
                exclude_today=config.get('exclude_today', False)
            )
        }
        if chart_format == 'png':
            del result['svg_data']
            result['slug'] = slugify(title)
        charts_data.append(result)

    return charts_data


def current_utc_time():
    return datetime.now()


def send_daily_digest():
    title = 'Daily Digest'
    config = getattr(settings, 'DAILY_DIGEST_CONFIG', {})
    if config.get('title'):
        title = config['title']

    today = current_utc_time().replace(tzinfo=los_angeles_timezone)
    subject = '{} - {}'.format(title, today.strftime('%x'))
    text_content = title

    context = {
        'charts': charts_data_for_config(chart_format='png')
    }

    html_template = get_template('daily_digest/email.html')
    html_content = html_template.render(context)

    msg = EmailMultiAlternatives(subject, text_content, config['from_email'], settings.ADMINS)
    msg.attach_alternative(html_content, "text/html")

    for chart in config.get('charts', []):
        slug = slugify(chart['title'])
        with open('/tmp/{}.png'.format(slug), 'rb') as image_file:
            msg_image = MIMEImage(image_file.read())
            msg_image.add_header('Content-ID', '<{}>'.format(slug))
            msg.attach(msg_image)

    msg.send(fail_silently=False)
