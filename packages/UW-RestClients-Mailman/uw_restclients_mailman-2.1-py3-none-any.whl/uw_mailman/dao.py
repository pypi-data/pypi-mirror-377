# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os
from os.path import abspath, dirname
from restclients_core.dao import DAO


class Mailman_DAO(DAO):
    def service_name(self):
        return 'mailman'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def _custom_headers(self, method, url, headers, body):
        api_token = self.get_service_setting('API_TOKEN', '')
        return {'Authorization': 'Token {}'.format(api_token)}
