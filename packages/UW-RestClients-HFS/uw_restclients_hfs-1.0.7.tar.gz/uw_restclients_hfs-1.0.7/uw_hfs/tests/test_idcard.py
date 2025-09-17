# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from datetime import datetime
from restclients_core.exceptions import DataFailureException
from uw_hfs.idcard import get_hfs_accounts

ADD_FUND_URL = ("https://www.hfs.washington.edu"
                "/olco/Secure/AccountSummary.aspx")


class TestHFSAccounts(TestCase):
    def test_get_accounts(self):
        hfs_acc = get_hfs_accounts("javerage")
        self.assertIsNotNone(hfs_acc.json_data(True))
        data = hfs_acc.student_husky_card.json_data(True)
        self.assertIsNotNone('add_funds_url' in data)
        self.assertIsNotNone('balance' in data)
        self.assertIsNotNone('last_updated' in data)
        self.assertIsNotNone('last_updated_dtime' in data)
        self.assertIsNotNone(str(hfs_acc.student_husky_card))
        self.assertEqual(hfs_acc.student_husky_card.last_updated,
                         datetime(2014, 6, 2, 15, 17, 16))
        self.assertEqual(hfs_acc.student_husky_card.balance, 1.23)
        self.assertEqual(hfs_acc.student_husky_card.add_funds_url,
                         ADD_FUND_URL)

        self.assertEqual(hfs_acc.employee_husky_card.last_updated,
                         datetime(2014, 5, 19, 14, 16, 26))
        self.assertEqual(hfs_acc.employee_husky_card.balance, 0.56)
        self.assertEqual(hfs_acc.employee_husky_card.add_funds_url,
                         ADD_FUND_URL)

        self.assertEqual(hfs_acc.resident_dining.last_updated,
                         datetime(2014, 6, 1, 13, 15, 36))
        self.assertEqual(hfs_acc.resident_dining.balance, 7.89)
        self.assertEqual(hfs_acc.resident_dining.add_funds_url,
                         ADD_FUND_URL)

    def test_get_hfs_empty_account(self):
        hfs_acc = get_hfs_accounts("eight")
        self.assertIsNotNone(hfs_acc.student_husky_card)
        self.assertIsNone(hfs_acc.employee_husky_card)
        self.assertIsNotNone(hfs_acc.resident_dining)

    def test_get_hfs_partially_empty_account(self):
        hfs_acc = get_hfs_accounts("jnew")
        self.assertIsNotNone(hfs_acc.student_husky_card)
        self.assertIsNone(hfs_acc.student_husky_card.last_updated)
        self.assertEqual(hfs_acc.student_husky_card.balance, 0.0)

        self.assertIsNone(hfs_acc.employee_husky_card)

        self.assertEqual(hfs_acc.resident_dining.balance, 777.89)
        self.assertEqual(hfs_acc.resident_dining.last_updated,
                         datetime(2014, 5, 17, 13, 15, 36))
        self.assertEqual(hfs_acc.resident_dining.add_funds_url,
                         ADD_FUND_URL)

    def test_invalid_user(self):
        # Testing error message in a 200 response
        self.assertRaises(DataFailureException,
                          get_hfs_accounts, "invalidnetid")
        self.assertRaises(DataFailureException,
                          get_hfs_accounts, "invalidnetid123")

        try:
            get_hfs_accounts("jerror")
        except DataFailureException as ex:
            self.assertEqual(ex.status, 500)
            self.assertEqual(ex.msg,
                             "An error has occurred.")
        try:
            get_hfs_accounts("none")
        except DataFailureException as ex:
            self.assertEqual(ex.status, 404)
            self.assertEqual(ex.msg,
                             "UWNetID none not found in IDCard Database.")

        MSG = ("Input for this method must be either a valid UWNetID "
               "or two nine-digit Student and "
               "Faculty/Staff/Employee ID numbers, comma-separated.")
        try:
            get_hfs_accounts("invalidnetid")
        except DataFailureException as ex:
            self.assertEqual(ex.status, 400)
            self.assertEqual(
                ex.msg, MSG)

    def test_float_parsing(self):
        hfs_acc = get_hfs_accounts("jbothell")
        self.assertEqual(hfs_acc.student_husky_card.balance, 5.1)
