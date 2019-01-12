import base64
import binascii
import configparser
import logging
import re
from os import path, chmod
from sys import exit, stderr
from xml.etree import ElementTree

import boto3

from oauth_cli.config import setting
from oauth_cli.saml.command import SAMLGetAccessTokenCommand


class AWSSTSGetCredentialsFromSAMLCommand(SAMLGetAccessTokenCommand):

    def __init__(self, account, role, profile):
        super(AWSSTSGetCredentialsFromSAMLCommand, self).__init__()
        self.account = account if account else setting.attributes.get('aws_account')
        self.role = role if role else setting.attributes.get('aws_role')
        self.profile = profile if profile else setting.attributes.get('aws_profile')
        self.saml_response = None
        self.statements = None

    namespaces = {'saml': 'urn:oasis:names:tc:SAML:2.0:assertion', 'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'}

    def get_attributes(self, saml_statement: ElementTree.Element):
        result = {}
        for attribute in saml_statement.findall('./saml:Attribute', self.namespaces):
            value: ElementTree.Element = attribute.find('./saml:AttributeValue', self.namespaces)
            result[attribute.get('Name')] = value.text
        return result

    def get_statements(self, root: ElementTree.Element):
        self.statements = []
        for statement in root.findall('.//saml:AttributeStatement', self.namespaces):
            self.statements.append(self.get_attributes(statement))
        self.get_roles()
        return self.statements

    def get_roles(self):
        role_name = 'https://aws.amazon.com/SAML/Attributes/Role'
        self.roles = {r[0]: r[1] for r in map(lambda r: r.split(','), map(lambda s: s[role_name],
                                                                          filter(lambda s: role_name in s,
                                                                                 self.statements)))}

    def parse_xml_response(self, saml_response) -> ElementTree.Element:
        result = None
        try:
            xml = base64.b64decode(saml_response)
            logging.debug(xml)
            result = ElementTree.fromstring(xml)
        except binascii.Error as e:
            logging.error('failed to parse the SAML response, %s', e)
            exit(1)
        except ElementTree.ParseError as e:
            logging.error('failed to parse the SAML response, %s', e.msg)
            exit(1)
        return result

    def set_saml_response(self, saml_response):
        self.saml_response = saml_response
        root = self.parse_xml_response(saml_response)
        self.get_statements(root)

    def print_roles(self):
        arn_pattern = re.compile(r'arn:aws:iam::(?P<account>[^:]*):role/(?P<role>.*)')
        for role in self.roles:
            stderr.write('\t{account}\t{role}\n'.format(**arn_pattern.match(role).groupdict()))

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
        logging.info(f'new credentials for {self.role} in account {self.account} have been written to ~/.aws/credentials')

    def run(self):
        if self.account and self.role and self.profile:
            self.request_authorization()
            self.assume_role()
        else:
            logging.error('--account, --role and --profile are required.')
            exit(1)
