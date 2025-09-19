# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.urls import re_path
from django_client_logger.views import LogReceiver


urlpatterns = [
    re_path(r'log', LogReceiver.as_view(), name='client_log_api')
]
