#
# Copyright 2019 - binx.io B.V.
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
import configparser
import re
from collections import namedtuple
from os import path, chmod

from auth0_login.logging import fatal

AWSAccount = namedtuple('AWSAccount', 'number alias')


class AWSAccountConfiguration(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read([path.expanduser(path.expandvars('~/.aws-accounts'))])
        self.accounts = self.config.defaults()

    def alias_for_account(self, account) -> str:
        """
        returns the alias for `account` from ~/.aws-accounts, or `account` if none found
        """
        return next(iter(filter(lambda k: str(self.accounts[k]) == str(account), self.accounts.keys())),
                    str(account))

    def account_for_alias(self, alias) -> str:
        """
        returns the account for `alias` from ~/.aws-accounts, or none if not found
        """
        return self.accounts.get(alias, None)

    def get_account(self, account) -> AWSAccount:
        if re.match(r'^[0-9]+$', account):
            result = AWSAccount(number=account, alias=self.alias_for_account(account))
        else:
            result = AWSAccount(number=self.account_for_alias(account), alias=account)
            if not result.number:
                fatal(f'{account} is not found in ~/.aws-accounts')
        return result




aws_accounts = AWSAccountConfiguration()
