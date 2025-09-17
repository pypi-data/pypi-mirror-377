# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.exceptions import DataFailureException
from uw_admin_systems.dao import AdminSystems_DAO


DAO = AdminSystems_DAO()


def get_resource(url):
    response = DAO.getURL(
        url, {"Accept": "application/json", "Connection": "keep-alive"}
    )
    data = (
        response.data.decode("UTF-8")
        if isinstance(response.data, bytes)
        else response.data
    )
    if response.status != 200:
        raise DataFailureException(url, response.status, data)
    return data
