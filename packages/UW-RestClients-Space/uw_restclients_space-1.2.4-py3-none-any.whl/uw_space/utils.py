# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from dateutil.parser import parse
from commonconf import override_settings

fdao_space_override = override_settings(
    RESTCLIENTS_SPACE_DAO_CLASS='Mock')


def str_to_datetime(s):
    return parse(s) if (s is not None and len(s)) else None


def date_to_str(dt):
    return str(dt) if dt is not None else None
