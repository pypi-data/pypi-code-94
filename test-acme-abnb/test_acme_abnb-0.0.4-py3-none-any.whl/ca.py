"""
Copyright 2021-present Airbnb, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import shutil
import subprocess
import requests
import sys
from typing import List

import boto3

from .logger import get_logger
from .client import get_secret


LOGGER = get_logger(__name__)


class LetsEncrypt:
    def __init__(self, hostname: str, subdelegate: str, subject_alternative_names: List[str], region: str) -> None:
        self.subdelegate = subdelegate
        self.region = region
        self.hostname = self._validate_device_connection(hostname)
        self.subject_alternative_names = self._validate_subdelegate_zone(
            subject_alternative_names)

    def _validate_device_connection(self, hostname, timeout=5):
        try:
            _ = requests.head(
                'https://{host}'.format(host=hostname), timeout=timeout, verify=False)
            _ = self._register_lets_encrypt_account()
            return hostname
        except requests.ConnectionError:
            raise Exception(
                "Failed Connection to Host: {}".format(hostname))

    def _validate_subdelegate_zone(self, subject_alternative_names: List[str]) -> None:
        client = boto3.client('route53')

        for hostname in subject_alternative_names:
            hosted_zone = os.environ['HOSTED_ZONE_ID']
            try:
                response = client.list_resource_record_sets(
                    HostedZoneId=hosted_zone,
                    StartRecordName='_acme-challenge.{hostname}'.format(
                        hostname=hostname),
                    StartRecordType='CNAME',
                    MaxItems='1'
                )['ResourceRecordSets'][0]['Name']

                if response != '_acme-challenge.{hostname}.'.format(hostname=hostname):
                    LOGGER.warning('Invalid Challenge Alias: {hostname}'.format(
                        hostname=hostname))
                    sys.exit(1)

            except Exception:
                raise Exception(
                    'Invalid FQDN: {hostname}'.format(hostname=hostname))

    def _register_lets_encrypt_account(self) -> None:
        prefix = os.environ['PREFIX']
        home = os.environ['HOME']
        region = os.environ['AWS_REGION']
        try:
            source_dir = "acme-v02.api.letsencrypt.org"
            acme_account = f"{home}/.acme.sh/ca/{source_dir}"
            if not os.path.exists(acme_account):
                os.makedirs(acme_account)

            account_json = get_secret(f'{prefix}/otter/account.json', region)
            with open('account.json', 'w') as outfile:
                outfile.write(account_json)
            account_key = get_secret(f'{prefix}/otter/account.key', region)
            with open('account.key', 'w') as outfile:
                outfile.write(account_key)

            ca_conf = get_secret(f'{prefix}/otter/ca.conf', region)
            with open('ca.conf', 'w') as outfile:
                outfile.write(ca_conf)

            shutil.move("account.json",
                        "{acme_account}/account.json".format(acme_account=acme_account))
            shutil.move("account.key",
                        "{acme_account}/account.key".format(acme_account=acme_account))
            shutil.move(
                "ca.conf", "{acme_account}/ca.conf".format(acme_account=acme_account))
        except Exception:
            message = 'ACME Account Binding Error on `{hostname}`.'.format(
                hostname=self.hostname)
            LOGGER.error(message)
            sys.exit(1)

    def acme_development(self, csr: str) -> None:
        subprocess.call(
            '{directory}/acme.sh/acme.sh --upgrade -b dev'.format(directory=os.getenv('HOME')), shell=True)
        subprocess.call('{directory}/acme.sh/acme.sh --set-default-ca --test --signcsr --csr {csr} --dns dns_aws --dnssleep 20 --challenge-alias {domain_validation} --preferred-chain "Fake LE Root X2" --force'.format(
            directory=os.getenv('HOME'), csr=f'{csr}', domain_validation=self.subdelegate), shell=True)

    def acme_production(self, csr: str) -> None:
        subprocess.call(
            '{directory}/acme.sh/acme.sh --upgrade'.format(directory=os.getenv('HOME')), shell=True)
        subprocess.call('{directory}/acme.sh/acme.sh --set-default-ca --server letsencrypt --signcsr --csr {csr} --dns dns_aws --dnssleep 20 --challenge-alias {domain_validation} --preferred-chain "ISRG Root X1" --force'.format(
            directory=os.getenv('HOME'), csr=f'{csr}', domain_validation=self.subdelegate), shell=True)

    def acme_local(self, csr: str) -> None:
        subprocess.call(
            '{directory}/.acme.sh/acme.sh --upgrade -b dev'.format(directory=os.getenv('HOME')), shell=True)
        subprocess.call('{directory}/.acme.sh/acme.sh --set-default-ca --test --signcsr --csr {csr} --dns dns_aws --dnssleep 20 --challenge-alias {domain_validation} --preferred-chain "Fake LE Root X2" --force'.format(
            directory=os.getenv('HOME'), csr=f'{csr}', domain_validation=self.subdelegate), shell=True)
