import pytz
import random
from datetime import datetime, timedelta, date
from django.contrib.auth.models import User
from project.photos.models import PhotoUpload

import mock
from django.test import TestCase
from django.test.client import Client

from .utils import EmailMultiAlternatives, send_daily_digest, series_data_for_model


class MockEmailMultiAlternatives(mock.Mock):
    subject = ''

    def __init__(self, subject, text_content, from_email, to):
        self.subject = subject
        self.text_content = text_content
        self.from_email = from_email
        self.to = to


class DailyDigestTestCase(TestCase):

    @mock.patch('daily_digest.utils.current_time_naive', return_value=datetime(2018, 1, 10, 8, 0))
    @mock.patch.object(EmailMultiAlternatives, 'send')
    @mock.patch.object(EmailMultiAlternatives, 'attach')
    @mock.patch.object(EmailMultiAlternatives, 'attach_alternative')
    @mock.patch.object(EmailMultiAlternatives, '__init__', return_value=None)
    def test_send_daily_digest(self, mock_init_email, mock_attach_html, mock_add_attachment, *_):
        send_daily_digest()

        subject, text_content, from_email, to_emails = mock_init_email.call_args_list[0][0]
        self.assertEqual(subject, 'Daily Digest - 01/10/18')
        self.assertEqual(text_content, 'Daily Digest')
        self.assertEqual(from_email, 'support@test.com')
        self.assertEqual(list(to_emails), [])
        self.assertEqual(
            mock_attach_html.call_args_list[0],
            mock.call('<!DOCTYPE html>\n<html>\n<head>\n\t<title></title>\n\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n\n\t</head>\n<body style="font-family:-apple-system, BlinkMacSystemFont, sans-serif">\n\t\n\n\n<h3 style="font-weight:500; margin-bottom:0">New Users</h3>\n\n\n\t<img class="chart" width="100%" src="cid:new-users" style="max-width:480px">\n\n<br>\n\n<h3 style="font-weight:500; margin-bottom:0">Photo Uploads</h3>\n\n\n\t<img class="chart" width="100%" src="cid:photo-uploads" style="max-width:480px">\n\n<br>\n\n\n\n</body>\n</html>\n', 'text/html')
        )
        self.assertEqual(mock_add_attachment.call_args_list[0][0][0].get('Content-ID'), '<new-users>')

    def test_daily_digest_preview(self):
        user = User.objects.create(username='test', is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()

        client = Client()
        client.login(username='test', password='test')

        response = client.get('/admin/daily-digest-preview/')
        self.assertEqual(response.status_code, 200)

    @mock.patch('daily_digest.utils.current_time_naive', return_value=datetime(2018, 1, 10, 16, 0))  # 8am LA
    def test_series_data_generated_for_current_period(self, *_):
        timezone = pytz.timezone('America/Los_Angeles')

        User.objects.filter(username__startswith='test').delete()
        PhotoUpload.objects.all().delete()
        los_angeles_timezone = pytz.timezone('America/Los_Angeles')
        today = los_angeles_timezone.localize(datetime(2018, 1, 10, 16, 0))

        for days in [-1, 0, 1, 2, 3, 4, 5, 6, 7]:
            for _ in range(0, days + 3):
                User.objects.create(username='test-{}'.format(random.randint(0, 100000000)), date_joined=today - timedelta(days=days))

        queryset = User.objects.all()

        data, total_count = series_data_for_model(
            queryset, 'date_joined', timezone
        )
        self.assertEqual(total_count, 42)
        self.maxDiff = None
        self.assertEqual(data, [
            [date(2018, 1, 4), 9], [date(2018, 1, 5), 8], [date(2018, 1, 6), 7],
            [date(2018, 1, 7), 6], [date(2018, 1, 8), 5], [date(2018, 1, 9), 4],
            [date(2018, 1, 10), 3]
        ])

    @mock.patch('daily_digest.utils.current_time_naive', return_value=datetime(2018, 1, 10, 16, 0))  # 8am LA
    def test_series_data_generated_for_previous_period(self, *_):
        timezone = pytz.timezone('America/Los_Angeles')

        User.objects.filter(username__startswith='test').delete()
        PhotoUpload.objects.all().delete()
        los_angeles_timezone = pytz.timezone('America/Los_Angeles')
        today = los_angeles_timezone.localize(datetime(2018, 1, 10, 16, 0))

        for days in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:
            for _ in range(0, days):
                User.objects.create(username='test-{}'.format(random.randint(0, 100000000)), date_joined=today - timedelta(days=days))

        queryset = User.objects.all()

        data, total_count = series_data_for_model(
            queryset, 'date_joined', timezone, prev_period=True
        )
        self.assertEqual(total_count, 70)
        self.maxDiff = None
        self.assertEqual(data, [
            [date(2018, 1, 4), 13], [date(2018, 1, 5), 12], [date(2018, 1, 6), 11],
            [date(2018, 1, 7), 10], [date(2018, 1, 8), 9], [date(2018, 1, 9), 8],
            [date(2018, 1, 10), 7]
        ])
