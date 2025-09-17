# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from restclients_core import models


class IDcardElig(models.Model):
    not_eligible = models.BooleanField(null=True, default=None)
    employee_eligible = models.BooleanField(null=True, default=None)
    retiree_eligible = models.BooleanField(null=True, default=None)
    student_eligible = models.BooleanField(null=True, default=None)

    def json_data(self):
        return {
            "not_eligible": self.not_eligible,
            "employee_eligible": self.employee_eligible,
            "retiree_eligible": self.retiree_eligible,
            "student_eligible": self.student_eligible,
        }

    @classmethod
    def create(cls, data):
        status = cls()
        emp_value = data.get("empCardElig", "")
        status.employee_eligible = emp_value == "Y"
        status.retiree_eligible = emp_value == "R"
        stud_value = data.get("stdtCardElig", "")
        status.student_eligible = stud_value == "Y"
        status.not_eligible = emp_value == "N" and stud_value == "N"
        return status

    def __str__(self):
        return json.dumps(self.json_data())


class UPassStatus(models.Model):
    active_employee_membership = models.BooleanField(null=True, default=None)
    active_student_membership = models.BooleanField(null=True, default=None)

    def json_data(self):
        return {
            "active_employee_membership": self.active_employee_membership,
            "active_student_membership": self.active_student_membership,
        }

    @classmethod
    def create(cls, data):
        status = cls()
        if "activeEmployeeMembership" in data:
            status.active_employee_membership = data.get(
                "activeEmployeeMembership", False
            )
        if "activeStudentMembership" in data:
            status.active_student_membership = data.get(
                "activeStudentMembership", False
            )
        return status

    def __str__(self):
        return json.dumps(self.json_data())
