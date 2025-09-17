# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_space import Facilities
from uw_space.utils import fdao_space_override

data = {
    'code': 'MEB',
    'last_updated': '2022-09-22 19:41:34',
    'latitude': 47.6536929997,
    'longitude': -122.304747,
    'name': 'Mechanical Engineering Building',
    'number': '1347',
    'site': 'Seattle Main Campus',
    'type': 'Building'
    }


@fdao_space_override
class TestSpace(TestCase):
    def test_search_by_code(self):
        fac = Facilities().search_by_code("MEB")
        self.assertEqual(len(fac), 1)
        data['status'] = 'A'
        self.assertEqual(fac[0].json_data(), data)

        self.assertRaises(
            DataFailureException,
            Facilities().search_by_code, "None"
        )

        fac = Facilities().search_by_code("MDR")
        self.assertEqual(len(fac), 1)
        self.assertEqual(fac[0].json_data(), {
            'code': 'MDR',
            'last_updated': '2022-09-22 12:49:38',
            'latitude': 47.6601320001,
            'longitude': -122.305391,
            'name': 'Madrona Hall',
            'number': '6471',
            'site': 'Seattle Main Campus',
            'status': 'A',
            'type': 'Building'
            })

    def test_search_by_number(self):
        fac = Facilities().search_by_number("1347")
        data['status'] = ''
        self.assertEqual(fac.json_data(), data)

        self.assertRaises(
            DataFailureException,
            Facilities().search_by_number, "0"
        )
