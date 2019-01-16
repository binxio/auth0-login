import base64
import binascii
import configparser
import logging
import re
from os import chmod, path
from sys import stdout
from typing import List
from xml.etree import ElementTree

import boto3
import click

from oauth_cli.config import setting
from oauth_cli.aws.aws_console import open_aws_console
from oauth_cli.saml.command import SAMLGetAccessTokenCommand


class AWSSTSGetCredentialsFromSAMLCommand(SAMLGetAccessTokenCommand):
    """
    get AWS credentials using the obtained SAML token and
    stores then in `~/.aws/credentials`.

    As multiple AWS roles may have been granted to the SAML token,
    the caller has to specify the `account` number and `role` name to
    generate the credentials for. If you are unsure which accounts
    and roles have been granted, use the `--show` option

    The credentials will be stored under the specified `profile` name.
    By specifying `--open-console` it will open the AWS console too.
    """

    def __init__(self, account, role, profile):
        super(AWSSTSGetCredentialsFromSAMLCommand, self).__init__()
        self.account = account if account else setting.attributes.get('aws_account')
        self.role = role if role else setting.attributes.get('aws_role')
        self.profile = profile if profile else setting.attributes.get('aws_profile')
        self.saml_response = None
        self.statements = None
        self.open_console = setting.attributes.get('aws_console', False)

    namespaces = {'saml': 'urn:oasis:names:tc:SAML:2.0:assertion', 'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'}

    def get_attributes(self, saml_statement: ElementTree.Element):
        result = {}
        for attribute in saml_statement.findall('./saml:Attribute', self.namespaces):
            value: List[ElementTree.Element] = attribute.findall('./saml:AttributeValue', self.namespaces)
            result[attribute.get('Name')] = list(map(lambda v: v.text, value))
        return result

    def get_statements(self, root: ElementTree.Element):
        self.statements = []
        for statement in root.findall('.//saml:AttributeStatement', self.namespaces):
            self.statements.append(self.get_attributes(statement))
        self.get_roles()
        return self.statements

    def get_roles(self):
        role_name = 'https://aws.amazon.com/SAML/Attributes/Role'
        roles = next(iter(map(lambda s: s[role_name], filter(lambda s: role_name in s, self.statements))), [])
        self.roles = {r[0]: r[1] for r in map(lambda r: r.split(','), roles)}

    def parse_xml_response(self, saml_response) -> ElementTree.Element:
        result = None
        try:
            xml = base64.b64decode(saml_response)
            logging.debug(xml)
            result = ElementTree.fromstring(xml)
        except binascii.Error as e:
            logging.fatal('failed to parse the SAML response, %s', e)
        except ElementTree.ParseError as e:
            logging.fatal('failed to parse the SAML response, %s', e.msg)
        return result

    def set_saml_response(self, saml_response):
        self.saml_response = saml_response
        root = self.parse_xml_response(saml_response)
        self.get_statements(root)

    def print_roles(self):
        arn_pattern = re.compile(r'arn:aws:iam::(?P<account>[^:]*):role/(?P<role>.*)')
        for role in self.roles:
            match = arn_pattern.match(role)
            if match:
                stdout.write(f'oauth-cli ')
                if setting.SECTION != 'DEFAULT':
                    stdout.write(f'-c {setting.SECTION} ')
                role = match.group('role')
                account = match.group('account')
                profile = self.profile if self.profile else f'{role}@{account}'
                stdout.write(f'aws-saml-assume-role --profile {profile} --acount {account} --role {role}\n')
            else:
                logging.error('expected a role arn, found %s', role)

    def show_account_roles(self):
        self.request_authorization()
        self.print_roles()

    def assume_role(self):
        role_arn = f'arn:aws:iam::{self.account}:role/{self.role}'
        sts = boto3.client('sts')
        response = sts.assume_role_with_saml(
            RoleArn=role_arn,
            PrincipalArn=self.roles[role_arn],
            SAMLAssertion=self.saml_response,
            DurationSeconds=setting.ROLE_DURATION
        )
        filename = path.expanduser(path.expandvars('~/.aws/credentials'))
        config = configparser.ConfigParser()
        config.read(filename)
        if not config.has_section(self.profile):
            config.add_section(self.profile)
        config.set(self.profile, 'aws_access_key_id', response['Credentials']['AccessKeyId'])
        config.set(self.profile, 'aws_secret_access_key', response['Credentials']['SecretAccessKey'])
        config.set(self.profile, 'aws_session_token', response['Credentials']['SessionToken'])
        config.set(self.profile, 'expiration', str(response['Credentials']['Expiration']))
        with open(filename, 'w') as f:
            config.write(f)
        chmod(filename, 0o600)
        logging.info(
            f'credentials for {self.role} in account {self.account} have been written in AWS profile {self.profile}.')

    def run(self):
        if self.account and self.role and self.profile:
            self.request_authorization()
            self.assume_role()
            if self.open_console:
                open_aws_console(self.profile)
        else:
            logging.fatal('--account, --role and --profile are required.')


@click.command('aws-saml-assume-role', help=AWSSTSGetCredentialsFromSAMLCommand.__doc__)
@click.option('--account', help='aws account number')
@click.option('--role', help='to assume using the token')
@click.option('--profile', help='to store the credentials under')
@click.option('--show', is_flag=True, default=False, help='account roles available to assume')
@click.option('--open-console', '-C', count=True, help=' after credential refresh')
def assume_role_with_saml(account, role, profile, show, open_console):
    cmd = AWSSTSGetCredentialsFromSAMLCommand(account, role, profile)
    if show:
        cmd.show_account_roles()
    else:
        if open_console:
            cmd.open_console = True
        cmd.run()
