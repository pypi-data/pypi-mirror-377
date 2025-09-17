# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with the mailman web service.
"""

import logging
from uw_mailman.dao import Mailman_DAO
from restclients_core.exceptions import DataFailureException


logger = logging.getLogger(__name__)


def get_resource(url):
    response = Mailman_DAO().getURL(url, {'Accept': 'application/json'})
    logger.debug("GET {} ==status==> {}".format(url, response.status))

    response_data = str(response.data)
    if response.status != 200:
        raise DataFailureException(url, response.status, response_data)

    logger.debug("GET {} ==data==> {}".format(url, response_data))
    return response.data
