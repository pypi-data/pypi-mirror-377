# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the mailman uwnetid resource
"""
from uw_mailman.basic_list import exists

COURSE_LIST_NAME = "{prefix}{curr_abbr}{course_no}{section_id}_{quarter}{year}"


def _get_list_name_curr_abbr(curriculum_abbr):
    """
    @return mailman specific curriculum abbr
    """
    return curriculum_abbr.lower().replace(' ', '').replace('&', '')


def get_course_list_name(curriculum_abbr, course_number, section_id,
                         quarter, year, joint=False):
    """
    Return the list address of UW course email list
    """
    prefix = "multi_" if (joint is True) else ""
    return COURSE_LIST_NAME.format(
        prefix=prefix,
        curr_abbr=_get_list_name_curr_abbr(curriculum_abbr),
        course_no=course_number,
        section_id=section_id.lower(),
        quarter=quarter.lower()[:2],
        year=str(year)[-2:]
    )


def exists_course_list(curriculum_abbr, course_number, section_id,
                       quarter, year, joint=False):
    """
    Return True if the corresponding mailman list exists for the course
    """
    return exists(get_course_list_name(curriculum_abbr, course_number,
                                       section_id, quarter, year, joint))


def get_section_list_name(section):
    """
    Return the list address of UW course section email list
    """
    return get_course_list_name(section.curriculum_abbr,
                                section.course_number,
                                section.section_id,
                                section.term.quarter,
                                section.term.year)


def exists_section_list(course_section):
    """
    Return True if the corresponding mailman list exists
    for the course section
    @param course_section a valid Section object
    """
    return exists(get_section_list_name(course_section))


def get_secondary_combined_list_name(curriculum_abbr,
                                     course_number,
                                     primary_section_id,
                                     quarter,
                                     year):
    return COURSE_LIST_NAME.format(
        prefix="multi_",
        curr_abbr=_get_list_name_curr_abbr(curriculum_abbr),
        course_no=course_number,
        section_id=primary_section_id.lower(),
        quarter=quarter.lower()[:2],
        year=str(year)[-2:]
    )


def exists_secondary_combined_list(curriculum_abbr,
                                   course_number,
                                   primary_section_id,
                                   quarter,
                                   year):
    """
    Return True if a combined mailman list exists for all
    the secondary course sections in the given quarter and year
    """
    return exists(get_secondary_combined_list_name(curriculum_abbr,
                                                   course_number,
                                                   primary_section_id,
                                                   quarter,
                                                   year))


def get_section_secondary_combined_list_name(section):
    if section.is_primary_section:
        section_id = section.section_id
    else:
        section_id = section.primary_section_id

    return get_secondary_combined_list_name(section.curriculum_abbr,
                                            section.course_number,
                                            section_id,
                                            section.term.quarter,
                                            section.term.year)


def exists_section_secondary_combined_list(course_section):
    """
    Return True if a combined mailman list exists
    for all the secondary course sections
    """
    return exists(
        get_section_secondary_combined_list_name(course_section))
