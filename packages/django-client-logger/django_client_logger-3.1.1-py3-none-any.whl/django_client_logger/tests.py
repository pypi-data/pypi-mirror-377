# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from userservice.user import UserServiceMiddleware
from django_client_logger.views import LogReceiver
from django_client_logger.logger import process_log_message
import logging
import mock


security = 'django.middleware.security.SecurityMiddleware'
Session = 'django.contrib.sessions.middleware.SessionMiddleware'
Common = 'django.middleware.common.CommonMiddleware'
CsrfView = 'django.middleware.csrf.CsrfViewMiddleware'
Auth = 'django.contrib.auth.middleware.AuthenticationMiddleware'
Message = 'django.contrib.messages.middleware.MessageMiddleware'
XFrame = 'django.middleware.clickjacking.XFrameOptionsMiddleware'
UserService = 'userservice.user.UserServiceMiddleware'
AUTH_BACKEND = 'django.contrib.auth.backends.RemoteUserBackend'
standard_test_override = override_settings(
    MIDDLEWARE=[Session,
                Common,
                CsrfView,
                Auth,
                Message,
                XFrame,
                UserService],
    AUTHENTICATION_BACKENDS=(AUTH_BACKEND,))


@standard_test_override
class TestLoggerAPI(TestCase):

    def setUp(self):
        self.request = RequestFactory().get("/")
        self.client = Client()
        self.request.session = self.client.session
        self.middleware = UserServiceMiddleware()
        self.middleware.process_request(self.request)
        self.client.session.save()

    def test_log_api(self):
        logger = logging.getLogger('TEST')
        with mock.patch.object(logger, 'info') as mock_logger:
            form = {'data': (
                '[{"logger": "TEST", "timestamp": 1517531326989, '
                '"level": "INFO", "message": ""}]')}
            response = self.client.post(reverse('client_log_api'), data=form)
            mock_logger.assert_called_once()

    def test_log_multiple_api(self):
        logger = logging.getLogger('TEST')
        with mock.patch.object(logger, 'info') as mock_logger:
            form = {'data': (
                '[{"logger": "TEST", "timestamp": 1517531326989, '
                '"level": "INFO", "message": ""},'
                '{"logger": "TEST", "timestamp": 1517531326999, '
                '"level": "INFO", "message": ""},'
                '{"logger": "TEST", "timestamp": 1517531327000, '
                ' "level": "INFO", "message": ""}]')}

            response = self.client.post(reverse('client_log_api'), data=form)
            self.assertEqual(mock_logger.call_count, 3)

    def test_log_error(self):
        logger = logging.getLogger('django_client_logger.views')
        with mock.patch.object(logger, 'error') as mock_logger:
            form = {'data': ''}
            response = self.client.post(reverse('client_log_api'), data=form)
            mock_logger.assert_called_once()


class TestLogResponse(TestCase):
    logger = logging.getLogger('INFO')
    with mock.patch.object(logger, 'info') as mock_logger:
        data = [{'logger': "INFO"}]
        process_log_message(data,
                            "1234",
                            "overrideuser",
                            "originaluser")
        log_data = {'original_user': 'originaluser',
                    'logger': 'INFO',
                    'session_key': '81dc9bdb52d04dc20036dbd8313ed055',
                    'override_user': 'overrideuser'}
        mock_logger.assert_called_with(log_data)
