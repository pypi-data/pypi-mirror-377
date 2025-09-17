# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.util.decorators import use_mock
from uw_mailman.dao import Mailman_DAO


fdao_mailman_override = use_mock(Mailman_DAO())
