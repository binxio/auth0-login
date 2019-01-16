import base64
import binascii
import configparser
import logging
import re
from collections import namedtuple
from os import chmod, path
from typing import List, Pattern
from xml.etree import ElementTree

import boto3
from botocore.exceptions import ClientError

AvailableRole = namedtuple('AvailableRole', 'provider account name arn')


class AWSSAMLAssertion(object):

    def __init__(self, saml_response):
        self.saml_response = saml_response
        self.root = self.parse_xml_response(saml_response)
        self.statements = self.get_statements(self.root)
        self.roles = self.get_roles(self.statements)

    namespaces = {'saml': 'urn:oasis:names:tc:SAML:2.0:assertion', 'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'}

    def get_attributes(self, saml_statement: ElementTree.Element):
        result = {}
        for attribute in saml_statement.findall('./saml:Attribute', self.namespaces):
            value: List[ElementTree.Element] = attribute.findall('./saml:AttributeValue', self.namespaces)
            result[attribute.get('Name')] = list(map(lambda v: v.text, value))
        return result

    def get_statements(self, root: ElementTree.Element) -> List[ElementTree.Element]:
        """
        returns all SAML attribute statements from the saml_response.
        """
        statements = []
        for statement in root.findall('.//saml:AttributeStatement', self.namespaces):
            statements.append(self.get_attributes(statement))
        return statements

    def get_roles(self, statements: List[ElementTree.Element]) -> dict:
        """
        returns all AWS roles from the SAML attribute statements.
        """
        role_name = 'https://aws.amazon.com/SAML/Attributes/Role'
        roles = next(iter(map(lambda s: s[role_name], filter(lambda s: role_name in s, statements))), [])
        return {r[0]: r[1] for r in map(lambda r: r.split(','), roles)}

    def parse_xml_response(self, saml_response: str) -> ElementTree.Element:
        """
        returns the XML root node of the SAML response, as returned by the SAML idp.
        """
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

    role_arn_pattern: Pattern = re.compile(r'arn:aws:iam::(?P<account>[^:]*):role/(?P<name>.*)')

    def available_roles(self) -> List[AvailableRole]:
        result = []
        for role in self.roles:
            match = self.role_arn_pattern.match(role)
            if match:
                result.append(AvailableRole(arn=role, provider=self.roles[role], account=match.group('account'),
                                            name=match.group('name')))
            else:
                logging.fatal('expected a role arn, found %s', role)
        return result

    def assume_role(self, role_arn, profile='default', duration=3600):
        if not role_arn or role_arn not in self.roles:
            logging.fatal('Role {role_arn} not granted')

        sts = boto3.client('sts')
        try:
            response = sts.assume_role_with_saml(
                RoleArn=role_arn,
                PrincipalArn=self.roles[role_arn],
                SAMLAssertion=self.saml_response,
                DurationSeconds=duration
            )
        except ClientError as e:
            logging.fatal('failed to assume role {role_arn}, %s', e)
        filename = path.expanduser(path.expandvars('~/.aws/credentials'))
        config = configparser.ConfigParser()
        config.read(filename)
        if not config.has_section(profile):
            config.add_section(profile)
        config.set(profile, 'aws_access_key_id', response['Credentials']['AccessKeyId'])
        config.set(profile, 'aws_secret_access_key', response['Credentials']['SecretAccessKey'])
        config.set(profile, 'aws_session_token', response['Credentials']['SessionToken'])
        config.set(profile, 'expiration', str(response['Credentials']['Expiration']))
        with open(filename, 'w') as f:
            config.write(f)
        chmod(filename, 0o600)
        logging.info(
            f'credentials for role {role_arn} saved under AWS profile {profile}.')
