import base64
import binascii
import configparser
import logging
import re
from collections import namedtuple
from os import chmod, path
from typing import Dict, List, Pattern
from xml.etree import ElementTree

import boto3
from botocore.exceptions import ClientError

from auth0_login import fatal

AvailableRole = namedtuple('AvailableRole', 'provider account name arn')


class AWSSAMLAssertion(object):

    def __init__(self, saml_response):
        self.saml_response: str = saml_response
        self.root: ElementTree.Element = self.parse_xml_response(saml_response)
        self.statements: List[Dict[str, List[str]]] = self.get_statements(self.root)
        self.roles: Dict[str, AvailableRole] = self.get_roles(self.statements)

    namespaces = {'saml': 'urn:oasis:names:tc:SAML:2.0:assertion', 'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'}

    @staticmethod
    def get_attributes(saml_statement: ElementTree.Element) -> Dict[str, List[str]]:
        result = {}
        for attribute in saml_statement.findall('./saml:Attribute', AWSSAMLAssertion.namespaces):
            value: List[ElementTree.Element] = attribute.findall('./saml:AttributeValue', AWSSAMLAssertion.namespaces)
            result[attribute.get('Name')] = list(map(lambda v: v.text, value))
        return result

    @staticmethod
    def get_statements(root: ElementTree.Element) -> List[Dict[str, List[str]]]:
        """
        returns all SAML attribute values from the saml_response.
        """
        statements = []
        for statement in root.findall('.//saml:AttributeStatement', AWSSAMLAssertion.namespaces):
            if isinstance(statement, ElementTree.Element):
                statements.append(AWSSAMLAssertion.get_attributes(statement))
            else:
                fatal('malformed XML: AttributeStatement {statement} is not a XML element')
        return statements

    @staticmethod
    def get_roles(statements:  List[Dict[str, List[str]]]) -> Dict[str, str]:
        """
        returns dictionary of AWS role ARN to AWS Provider ARN from the SAML attribute statements.
        """
        role_name = 'https://aws.amazon.com/SAML/Attributes/Role'
        roles = next(iter(map(lambda s: s[role_name], filter(lambda s: role_name in s, statements))), [])
        return {r[0]: r[1] for r in map(lambda r: r.split(','), roles)}

    @staticmethod
    def parse_xml_response(saml_response: str) -> ElementTree.Element:
        """
        returns the XML root node of the SAML response, as returned by the SAML idp.
        """
        result = None
        try:
            xml = base64.b64decode(saml_response)
            logging.debug(xml)
            result = ElementTree.fromstring(xml)
        except binascii.Error as e:
            fatal('failed to parse the SAML response, %s', e)
        except ElementTree.ParseError as e:
            fatal('failed to parse the SAML response, %s', e.msg)
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
                fatal('expected a role arn, found %s', role)
        return result

    def assume_role(self, role_arn, profile='default', duration=3600):
        if not role_arn or role_arn not in self.roles:
            available_roles = ', '.join(self.roles.keys())
            fatal(f'Role {role_arn} not granted, choose one of {available_roles}')

        sts = boto3.client('sts')
        try:
            response = sts.assume_role_with_saml(
                RoleArn=role_arn,
                PrincipalArn=self.roles[role_arn],
                SAMLAssertion=self.saml_response,
                DurationSeconds=duration
            )
        except ClientError as e:
            fatal('failed to assume role {role_arn}, %s', e)
            return
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
