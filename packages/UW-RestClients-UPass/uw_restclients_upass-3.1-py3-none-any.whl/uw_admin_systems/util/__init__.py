# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.util.decorators import use_mock
from uw_admin_systems import DAO


fdao_uw_admin_sys_override = use_mock(DAO)
