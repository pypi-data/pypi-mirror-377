# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


import json
import logging
from restclients_core.exceptions import DataFailureException
from uw_space.dao import SPACE_DAO
from uw_space.models import Facility

by_code_path = "/space/v2/facility.json?facility_code={}"
by_number_path = "/space/v2/facility/{}.json"
logger = logging.getLogger(__name__)


class Facilities(object):

    def __init__(self):
        self.dao = SPACE_DAO()
        self._read_headers = {
            'Accept': 'application/json',
            'Connection': 'keep-alive'}

    def search_by_code(self, facility_code):
        """
        facility_code: string
        """
        url = by_code_path.format(facility_code)
        response = self.dao.getURL(url, self._read_headers)
        logger.debug(
            {'url': url, 'status': response.status, 'data': response.data})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)
        return self.__process_json(json.loads(response.data))

    def search_by_number(self, facility_number):
        """
        facility_number: string
        """
        url = by_number_path.format(facility_number)
        response = self.dao.getURL(url, self._read_headers)
        logger.debug(
            {'url': url, 'status': response.status, 'data': response.data})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)
        return Facility.from_json(json.loads(response.data))

    def __process_json(self, json_data):
        objs = []
        facilities = json_data.get("Facilities")
        if facilities:
            for facility in facilities:
                status = facility.get("Status")
                fnumber = facility.get("FacilityNumber")
                if fnumber and len(fnumber):
                    fac = self.search_by_number(fnumber)
                    if fac:
                        fac.status = status
                        objs.append(fac)
        return objs
