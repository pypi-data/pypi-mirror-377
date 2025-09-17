# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the mailman uwnetid resource
"""

import json
from uw_mailman import get_resource


URL = "/uw_list_manager/api/v1/list/{list_name}/exists"


def _get_url_path(list_name):
    """
    existance test url for given list name
    """
    return URL.format(list_name=list_name)


def get_list_by_name(list_name):
    """
    Return the mailman list object for the given list name string
    @param list_name: a non_empty string
    """
    return json.loads(get_resource(_get_url_path(list_name)))


def exists(list_name):
    """
    Return True if the corresponding mailman list already exists
    for the given list name string
    @param list_name: a non_empty string
    """
    mlist = get_list_by_name(list_name)
    return mlist.get('exists', False)


def get_admin_url(list_name):
    mlist = get_list_by_name(list_name)
    return mlist.get("admin_url", "")
