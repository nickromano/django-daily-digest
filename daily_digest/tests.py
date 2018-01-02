import mock
from django.test import TestCase

from .utils import EmailMultiAlternatives, send_daily_digest


class MockEmailMultiAlternatives(mock.Mock):
    subject = ''

    def __init__(self, subject, text_content, from_email, to):
        self.subject = subject
        self.text_content = text_content
        self.from_email = from_email
        self.to = to


class DailyDigestTestCase(TestCase):

    @mock.patch.object(EmailMultiAlternatives, 'send')
    @mock.patch.object(EmailMultiAlternatives, 'attach')
    @mock.patch.object(EmailMultiAlternatives, 'attach_alternative')
    @mock.patch.object(EmailMultiAlternatives, '__init__', return_value=None)
    def test_send_daily_digest(self, mock_init_email, mock_attach_html, mock_add_attachment, *_):
        send_daily_digest()

        self.assertEqual(
            mock_init_email.call_args_list[0],
            mock.call('Daily Digest - 01/02/18', 'Daily Digest', 'support@test.com', [])
        )
        self.assertEqual(
            mock_attach_html.call_args_list[0],
            mock.call('<!DOCTYPE html>\n<html>\n<head>\n\t<title></title>\n\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n</head>\n<body>\n\t\n\n\n<h3 style="\n    font-weight: 500;\n    font-family: -apple-system, BlinkMacSystemFont, sans-serif;\n    margin-bottom: 0;\n    ">New Users</h3>\n\n\n\t<img style="max-width: 480px;" width="100%" src="cid:new-users"/>\n\n<br />\n\n\n\n</body>\n</html>\n', 'text/html')
        )
        self.assertEqual(mock_add_attachment.call_args_list[0][0][0].get('Content-ID'), '<new-users>')
