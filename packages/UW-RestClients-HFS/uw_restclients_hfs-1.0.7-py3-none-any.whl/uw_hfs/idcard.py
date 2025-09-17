# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


"""
This is the interface for interacting with the HFS Web Service.
"""

import logging
import json
from dateutil.parser import parse
from uw_hfs.models import (
    StudentHuskyCardAccount, EmployeeHuskyCardAccount, ResidentDiningAccount,
    HfsAccounts)
from uw_hfs import get_resource

ACCOUNTS_URL = "/myuw/v1/{uwnetid}"
logger = logging.getLogger(__name__)


def get_hfs_accounts(netid):
    """
    Return a restclients.models.hfs.HfsAccounts object on the given uwnetid
    """
    url = ACCOUNTS_URL.format(uwnetid=netid)
    response = get_resource(url)
    return _object_from_json(response)


def _object_from_json(response_body):
    return_obj = HfsAccounts()
    json_data = json.loads(response_body)

    if json_data.get('student_husky_card') is not None:
        return_obj.student_husky_card = _load_acc_obj(
            json_data['student_husky_card'],
            StudentHuskyCardAccount())

    if json_data.get('resident_dining') is not None:
        return_obj.resident_dining = _load_acc_obj(
            json_data['resident_dining'],
            ResidentDiningAccount())
    elif json_data.get('student_resident_dining') is not None:
        return_obj.resident_dining = _load_acc_obj(
            json_data['student_resident_dining'],
            ResidentDiningAccount())

    if json_data.get('employee_husky_card') is not None:
        return_obj.employee_husky_card = _load_acc_obj(
            json_data['employee_husky_card'],
            EmployeeHuskyCardAccount())

    return return_obj


def _load_acc_obj(account_data, account_obj):
    account_obj.balance = account_data.get('balance')
    account_obj.last_updated = _str_to_datetime(
        account_data.get('last_transaction_date'))
    account_obj.add_funds_url = account_data.get('add_funds_url')
    return account_obj


def _str_to_datetime(s):
    return parse(s) if (s is not None and len(s)) else None
