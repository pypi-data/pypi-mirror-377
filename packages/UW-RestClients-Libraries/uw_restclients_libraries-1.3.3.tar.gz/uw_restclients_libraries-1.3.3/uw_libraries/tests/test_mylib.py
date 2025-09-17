# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_libraries.mylib import get_account, get_account_html
from uw_libraries.util import fdao_mylib_override
from restclients_core.exceptions import DataFailureException


@fdao_mylib_override
class MyLibInfoTest(TestCase):
    def test_get_account(self):
        account = get_account("javerage")
        self.assertEqual(account.holds_ready, 1)
        self.assertEqual(account.fines, 5.35)
        self.assertEqual(account.items_loaned, 3)
        self.assertEqual(
            account.get_next_due_date_str(),
            "2020-10-15T02:00:00+00:00")
        self.assertIsNotNone(str(account))
        self.assertEqual(
            account.json_data(),
            {'holds_ready': 1,
             'fines': 5.35,
             'items_loaned': 3,
             'next_due': '2020-10-15T02:00:00+00:00'})

        account = get_account("jnewstudent")
        self.assertIsNone(account.next_due)
        self.assertEqual(account.holds_ready, 0)
        self.assertEqual(account.fines, 0.0)
        self.assertEqual(account.items_loaned, 0)

    def test_html_response(self):
        response = get_account_html("javerage")
        self.assertEqual(response, (
            b'<p>You have 7 items checked out.<br>\nYou have items '
            b'due back on 2014-04-29.<br>\nYou don\'t owe any fines.</p>\n<a '
            b'href="http://alliance-primo.hosted.exlibrisgroup.com/'
            b'primo_library/libweb/action/dlBasketGet.do?vid=UW&redirectTo='
            b'myAccount">Go to your account</a>'))

    def test_bad_json(self):
        self.assertRaises(Exception, get_account, "badjsonuser")

        try:
            get_account("badjsonuser")
            self.assertTrue(False, "Shouldn't get here")
        except Exception as ex:
            self.assertTrue("example bad data" in str(ex))

    def test_invalid_user(self):
        # Testing error message in a 200 response
        self.assertRaises(DataFailureException, get_account, "invalidnetid")
        # Testing non-200 response
        self.assertRaises(DataFailureException, get_account, "invalidnetid123")

        try:
            get_account("invalidnetid")
        except DataFailureException as ex:
            self.assertTrue("User not found" in str(ex.msg))

    def test_with_timestamp(self):
        response = get_account_html('javerage', timestamp=1391122522900)
        self.assertEqual(response, (
            b'<p>You have 7 items checked out.<br>\n You have items '
            b'due back on 2014-04-29.<br>\n You don\'t owe any fines.</p>\n '
            b'<a href="http://alliance-primo.hosted.exlibrisgroup.com/'
            b'primo_library/libweb/action/dlBasketGet.do?vid=UW&amp;'
            b'redirectTo=myAccount">Go to your account</a>'))
