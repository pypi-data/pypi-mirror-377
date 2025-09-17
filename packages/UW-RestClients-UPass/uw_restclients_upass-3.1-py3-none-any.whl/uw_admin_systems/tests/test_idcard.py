# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_admin_systems.idcard import get_idcard_elig
from restclients_core.exceptions import DataFailureException
from uw_admin_systems.util import fdao_uw_admin_sys_override


@fdao_uw_admin_sys_override
class IdcardTest(TestCase):
    def test_get_idcard_elig(self):
        status = get_idcard_elig("javerage")
        self.assertEqual(
            status.json_data(),
            {
                "not_eligible": False,
                "student_eligible": True,
                "retiree_eligible": False,
                "employee_eligible": True
            }
        )
        self.assertIsNotNone(str(status))

        status = get_idcard_elig("staff")
        self.assertTrue(status.employee_eligible)
        self.assertFalse(status.student_eligible)

        status = get_idcard_elig("retiree")
        self.assertTrue(status.retiree_eligible)
        self.assertFalse(status.employee_eligible)
        self.assertFalse(status.student_eligible)

        status = get_idcard_elig("none")
        self.assertTrue(status.not_eligible)
        self.assertFalse(status.employee_eligible)
        self.assertFalse(status.student_eligible)

        self.assertRaises(DataFailureException,
                          get_idcard_elig,
                          "notexist")
