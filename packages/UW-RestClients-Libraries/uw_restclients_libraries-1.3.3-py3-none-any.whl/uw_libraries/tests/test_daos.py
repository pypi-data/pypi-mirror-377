# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_libraries.dao import MyLib_DAO, SubjectGuide_DAO


class TestDao(TestCase):

    def test_mylib_dao(self):
        self.assertEqual(MyLib_DAO().service_name(), "libraries")

    def test_subjectguide_dao(self):
        self.assertEqual(SubjectGuide_DAO().service_name(), "libcurrics")
