# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.exceptions import DataFailureException


class TermEvalNotCreated(DataFailureException):

    def __init__(self, url, status, msg):
        super(TermEvalNotCreated, self).__init__(url, status, msg)
