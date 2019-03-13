# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import leather
import pytz
from cairosvg import svg2png
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from email.mime.image import MIMEImage
from premailer import transform

from .config import daily_digest_config

leather.theme.background_color = '#ffffff'
leather.theme.title_font_family = 'Helvetica'
leather.theme.legend_font_family = 'Helvetica'
leather.theme.tick_font_family = 'Helvetica'
PRIMARY_STROKE_COLOR = '#4383CC'
PREV_PERIOD_STROKE_COLOR = '#B4CDEB'

EMAIL_TIME_PERIOD = 7


def current_time_naive():
    return datetime.now()


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
    return current_label.strip(), prev_period_label.strip()


def series_data_for_model(queryset, field, timezone, prev_period=False, exclude_today=False):
    start_of_today = timezone.localize(current_time_naive().replace(hour=0, minute=0, second=0))
    start_of_today = start_of_today.astimezone(pytz.UTC)

    if exclude_today:
        start_of_today = start_of_today - timedelta(days=1)

    start_of_today += timedelta(days=1)  # End of today
    if prev_period:
        period_end = start_of_today - timedelta(days=EMAIL_TIME_PERIOD)  # End of today
        period_start = period_end - timedelta(days=EMAIL_TIME_PERIOD)
    else:
        period_end = start_of_today
        period_start = period_end - timedelta(days=EMAIL_TIME_PERIOD)

    filters = {
        '{}__gte'.format(field): period_start,
        '{}__lt'.format(field): period_end
    }
    series_data = queryset.filter(**filters).values_list(
        field, flat=True
    )
    series_data = list(map(
        lambda x: x.astimezone(timezone).date(),
        series_data
    ))

    grouped_by_date = []
    period_start_local = period_start.astimezone(timezone)
    for i in range(0, EMAIL_TIME_PERIOD):
        day = (period_start_local + timedelta(days=i)).date()
        count = 0
        for user_date in series_data:
            if user_date == day:
                count += 1
        if prev_period:
            day = day + timedelta(days=EMAIL_TIME_PERIOD)  # offset date to show both series on one chart
        grouped_by_date.append([day, count])

    return grouped_by_date, len(series_data)


def svg_data_for_query(queryset, field, chart_name, timezone, exclude_today=False):
    data, total_count = series_data_for_model(
        queryset, field, timezone, exclude_today=exclude_today)
    data_prev_period, total_count_prev_period = series_data_for_model(
        queryset, field, timezone, prev_period=True, exclude_today=exclude_today)

    # Show every date on the x axis
    x_axis_ticks = []
    for item in data:
        x_axis_ticks.append(item[0])

    chart = leather.Chart()
    chart.add_x_axis(ticks=x_axis_ticks)

    # Start at 0 - Turn this into an option
    y_max = max([item[1] for item in data])
    y_max_prev_period = max([item[1] for item in data_prev_period])
    chart.add_y_scale(0, max([y_max, y_max_prev_period]))

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
    for chart_config in daily_digest_config.chart_configs:
        title = chart_config.title
        date_field = chart_config.date_field
        filter_kwargs = chart_config.filter_kwargs
        queryset = chart_config.model.objects.filter(**filter_kwargs)
        if chart_config.distinct_by:
            queryset = queryset.distinct(
                chart_config.distinct_by
            ).order_by(
                chart_config.distinct_by
            )
        result = {
            'title': title,
            'svg_data': svg_data_for_query(
                queryset, date_field, chart_config.slug,
                timezone=daily_digest_config.timezone,
                exclude_today=daily_digest_config.exclude_today
            )
        }
        if chart_format == 'png':
            del result['svg_data']
            result['slug'] = chart_config.slug
        charts_data.append(result)

    return charts_data


def send_daily_digest():
    title = daily_digest_config.title
    today = daily_digest_config.timezone.localize(current_time_naive())
    subject = '{} - {}'.format(title, today.strftime('%x'))
    text_content = title

    context = {
        'charts': charts_data_for_config(chart_format='png')
    }

    html_template = get_template('daily_digest/email.html')
    html_content = html_template.render(context)
    # Inline all css
    html_content = transform(html_content)

    msg = EmailMultiAlternatives(subject, text_content, daily_digest_config.from_email, daily_digest_config.to)
    msg.attach_alternative(html_content, "text/html")

    for chart_config in daily_digest_config.chart_configs:
        with open('/tmp/{}.png'.format(chart_config.slug), 'rb') as image_file:
            msg_image = MIMEImage(image_file.read())
            msg_image.add_header('Content-ID', '<{}>'.format(chart_config.slug))
            msg.attach(msg_image)

    msg.send(fail_silently=False)
