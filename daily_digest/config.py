import pytz
from collections import namedtuple
from django.conf import settings
from django.utils.text import slugify


class DailyDigestConfigurationException():
    pass


class DailyDigestRequiredFieldException(DailyDigestConfigurationException):
    pass


_config = getattr(settings, 'DAILY_DIGEST_CONFIG', {})


DailyDigestChart = namedtuple('DailyDigestChart', ['title', 'slug', 'app_label', 'model', 'date_field', 'filter_kwargs', 'distinct_by'])
_chart_configs = []
for chart in _config.get('charts', []):
    for key in ['title', 'app_label', 'model', 'date_field']:
        if not chart.get(key):
            raise DailyDigestRequiredFieldException('Missing required field {} for chart config.'.format(key))
    chart_config = DailyDigestChart(
        title=chart['title'],
        slug=slugify(chart['title']),
        app_label=chart['app_label'],
        model=chart['model'],
        date_field=chart['date_field'],
        filter_kwargs=chart.get('filter_kwargs', {}),
        distinct_by=chart.get('distinct_by')
    )
    _chart_configs.append(chart_config)


DailyDigestConfig = namedtuple('DailyDigestConfig', ['title', 'from_email', 'timezone', 'exclude_today', 'chart_configs'])
daily_digest_config = DailyDigestConfig(
    title=_config.get('title', 'Daily Digest'),
    from_email=_config.get('from_email', settings.DEFAULT_FROM_EMAIL),
    timezone=pytz.timezone(_config['timezone']) if _config.get('timezone') else pytz.UTC,
    exclude_today=_config.get('exclude_today', False),
    chart_configs=_chart_configs
)
