from collections import namedtuple

import importlib
import pytz
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify


class DailyDigestConfigurationException(Exception):
    pass


class DailyDigestRequiredFieldException(DailyDigestConfigurationException):
    pass


def import_class_at_path(path):
    module_name, class_name = path.rsplit('.', 1)
    parser_module = importlib.import_module(module_name)
    parser_class = getattr(parser_module, class_name)
    return parser_class


DailyDigestConfig = namedtuple('DailyDigestConfig', [
    'title', 'from_email', 'to', 'timezone', 'exclude_today', 'chart_configs'
])


def load_config():
    global daily_digest_config

    _config = getattr(settings, 'DAILY_DIGEST_CONFIG', {})

    DailyDigestChart = namedtuple('DailyDigestChart', ['title', 'slug', 'model', 'date_field', 'filter_kwargs', 'distinct_by'])
    _chart_configs = []
    for chart in _config.get('charts', []):
        for key in ['title', 'model', 'date_field']:
            if not chart.get(key):
                raise DailyDigestRequiredFieldException('Missing required field {} for chart config.'.format(key))

        if chart.get('app_label'):
            # Allow the user to pass an app_label and model
            content_type = ContentType.objects.get(app_label=chart['app_label'], model=chart['model'])
            model = content_type.model_class()
        else:
            model = import_class_at_path(chart['model'])

        chart_config = DailyDigestChart(
            title=chart['title'],
            slug=slugify(chart['title']),
            model=model,
            date_field=chart['date_field'],
            filter_kwargs=chart.get('filter_kwargs', {}),
            distinct_by=chart.get('distinct_by')
        )
        _chart_configs.append(chart_config)

    daily_digest_config = DailyDigestConfig(
        title=_config.get('title', 'Daily Digest'),
        from_email=_config.get('from_email', settings.DEFAULT_FROM_EMAIL),
        to=_config.get('to', settings.ADMINS),
        timezone=pytz.timezone(_config['timezone']) if _config.get('timezone') else pytz.UTC,
        exclude_today=_config.get('exclude_today', False),
        chart_configs=_chart_configs
    )


load_config()
