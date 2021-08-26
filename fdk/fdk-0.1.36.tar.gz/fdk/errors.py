#
# Copyright (c) 2019, 2020 Oracle and/or its affiliates. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from fdk import constants
from fdk import response


class DispatchException(Exception):

    def __init__(self, ctx, status, message):
        """
        JSON response with error
        :param status: HTTP status code
        :param message: error message
        """
        self.status = status
        self.message = message
        self.ctx = ctx

    def response(self):
        resp_headers = {
            constants.CONTENT_TYPE: "application/json; charset=utf-8",
        }
        return response.Response(
            self.ctx,
            response_data=self.message,
            headers=resp_headers,
            status_code=self.status
        )
