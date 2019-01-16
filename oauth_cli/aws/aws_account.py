import configparser
import logging
import re
from collections import namedtuple
from os import path

AWSAccount = namedtuple('AWSAccount', 'number alias')


class AWSAccountConfiguration(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read([path.expanduser(path.expandvars('~/.aws-accounts.ini'))])

    def alias_for_account(self, account) -> str:
        """
        returns the alias for `account` from ~/.aws-accounts.ini, or `account` if none found
        """
        return next(iter(filter(lambda k: str(self.aws_accounts[k]) == str(account), self.aws_accounts.keys())),
                    str(account))

    def account_for_alias(self, alias) -> str:
        """
        returns the account for `alias` from ~/.aws-accounts.ini, or none if not found
        """
        return self.config.defaults().get(alias, None)

    def get_account(self, account) -> AWSAccount:
        if re.match(r'^[0-9]+$', account):
            result = AWSAccount(number=account, alias=self.alias_for_account(account))
        else:
            result = AWSAccount(number=self.account_for_alias(account), alias=account)
            if not result.number:
                logging.fatal(f'{account} is not found in ~/.aws-accounts.ini')
        return result
