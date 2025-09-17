# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from restclients_core import models
from uw_hfs.util import past_datetime_str


class HFSAccount(models.Model):
    balance = models.DecimalField(max_digits=8, decimal_places=2)
    last_updated = models.DateTimeField(null=True, default=None)
    add_funds_url = models.CharField(max_length=80)

    def get_timestamp_str(self, use_custom_date_format):
        if self.last_updated is not None:
            if use_custom_date_format:
                return past_datetime_str(self.last_updated)
            else:
                return str(self.last_updated)

    def json_data(self, use_custom_date_format=False):
        return {
            'balance': self.balance,
            'last_updated_dtime': (str(self.last_updated) if
                                   self.last_updated else None),
            'last_updated': self.get_timestamp_str(use_custom_date_format),
            'add_funds_url': self.add_funds_url
        }

    def __str__(self):
        return json.dumps(self.json_data())


class StudentHuskyCardAccount(HFSAccount):
    pass


class EmployeeHuskyCardAccount(HFSAccount):
    pass


class ResidentDiningAccount(HFSAccount):
    pass


class HfsAccounts(models.Model):
    student_husky_card = models.ForeignKey(StudentHuskyCardAccount,
                                           on_delete=models.PROTECT,
                                           null=True,
                                           default=None
                                           )
    employee_husky_card = models.ForeignKey(EmployeeHuskyCardAccount,
                                            on_delete=models.PROTECT,
                                            null=True,
                                            default=None
                                            )
    resident_dining = models.ForeignKey(ResidentDiningAccount,
                                        on_delete=models.PROTECT,
                                        null=True,
                                        default=None
                                        )

    def json_data(self, use_custom_date_format=False):
        return_value = {'student_husky_card': None,
                        'employee_husky_card': None,
                        'resident_dining': None
                        }

        if self.student_husky_card is not None:
            return_value['student_husky_card'] =\
                self.student_husky_card.json_data(use_custom_date_format)

        if self.employee_husky_card is not None:
            return_value['employee_husky_card'] =\
                self.employee_husky_card.json_data(use_custom_date_format)

        if self.resident_dining is not None:
            return_value['resident_dining'] =\
                self.resident_dining.json_data(use_custom_date_format)

        return return_value
