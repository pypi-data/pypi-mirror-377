# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with the UW Libraries Web Service.
"""

from datetime import datetime
from dateutil.parser import parse
import json
from urllib.parse import urlencode
from uw_libraries.dao import MyLib_DAO
from uw_libraries.models import MyLibAccount
from restclients_core.exceptions import DataFailureException

MyLibDao = MyLib_DAO()
mylib_url_prefix = '/mylibinfo/v1/'


def _get_mylib_resource(url):
    response = MyLibDao.getURL(url, {})

    response_data = str(response.data)
    if response.status != 200:
        raise DataFailureException(url, response.status, response_data)

    # 'Bug' with lib API causing requests with no/invalid user to return a 200
    if "User not found" in response_data:
        raise DataFailureException(url, 404, response_data)

    return response.data


def _get_account(netid, timestamp=None, is_html=False):
    params = [("id", netid)]
    if timestamp is not None:
        params.append(("timestamp", timestamp))
    if is_html:
        params.append(("style", "html"))

    url = "{}?{}".format(mylib_url_prefix, urlencode(params))
    return _get_mylib_resource(url)


def get_account(netid, timestamp=None):
    """
    The Libraries object has a method for getting information
    about a user's library account
    """
    response = _get_account(netid, timestamp=timestamp)
    return _account_from_json(response)


def get_account_html(netid, timestamp=None):
    """
    The Libraries object has a method for getting information
    about a user's library account
    """
    return _get_account(netid, timestamp=timestamp, is_html=True)


def _account_from_json(body):
    try:
        account_data = json.loads(body)
    except Exception as ex:
        raise Exception(
            "Unable to parse mylibinfo: {}. {}".format(body, ex))
    account = MyLibAccount()
    account.fines = account_data["fines"]
    account.holds_ready = account_data["holds_ready"]
    account.items_loaned = account_data["items_loaned"]
    account.next_due = account_data.get("next_due_utc")
    if account.next_due is not None:
        account.next_due = parse(account.next_due)
    return account
