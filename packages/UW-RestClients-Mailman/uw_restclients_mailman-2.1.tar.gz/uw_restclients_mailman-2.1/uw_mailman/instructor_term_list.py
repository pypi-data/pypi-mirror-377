# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the mailman uwnetid resource
"""

from uw_mailman.basic_list import exists


def get_instructor_term_list_name(instructor_netid, year, quarter):
    """
    Return the list address of UW instructor email list for
    the given year and quarter
    """
    return "{uwnetid}_{quarter}{year}".format(
        uwnetid=instructor_netid,
        quarter=quarter.lower()[:2],
        year=str(year)[-2:])


def exists_instructor_term_list(instructor_netid, year, quarter):
    """
    Return True if a combined mailman list exists for all courses
    taught by the UW instructor in the given term
    """
    return exists(get_instructor_term_list_name(instructor_netid,
                                                year, quarter))
