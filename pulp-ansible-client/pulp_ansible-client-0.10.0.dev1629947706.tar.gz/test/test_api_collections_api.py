# coding: utf-8

"""
    Pulp 3 API

    Fetch, Upload, Organize, and Distribute Software Packages  # noqa: E501

    The version of the OpenAPI document: v3
    Contact: pulp-list@redhat.com
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import pulpcore.client.pulp_ansible
from pulpcore.client.pulp_ansible.api.api_collections_api import ApiCollectionsApi  # noqa: E501
from pulpcore.client.pulp_ansible.rest import ApiException


class TestApiCollectionsApi(unittest.TestCase):
    """ApiCollectionsApi unit test stubs"""

    def setUp(self):
        self.api = pulpcore.client.pulp_ansible.api.api_collections_api.ApiCollectionsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get(self):
        """Test case for get

        """
        pass

    def test_post(self):
        """Test case for post

        """
        pass


if __name__ == '__main__':
    unittest.main()
