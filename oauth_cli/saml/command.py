import json
import logging
import configparser
import hashlib
import webbrowser
from base64 import urlsafe_b64encode
from http.server import HTTPServer
from os import path, chmod
from random import getrandbits
from sys import exit, stderr, stdout
from urllib.parse import urlencode, urlparse
from uuid import uuid4

from oauth_cli.saml.callback import SAMLAccessTokenCallbackhandler


class SAMLGetAccessTokenCommand(object):
    def __init__(self):
        self.api = "DEFAULT"
        self.saml_idp_url = None
        self.saml_callback_url = None
        self.listen_address = None
        self.listen_port = None
        self.defaults = {'listen_address': '0.0.0.0'}
        self.saml_response_file = path.expandvars(path.expanduser('~/.aws/saml-response'))
        self.tokens = {}


    def determine_listen_port(self):
        result = urlparse(self.saml_callback_url)
        netloc = result.netloc.split(':')
        if len(netloc) == 2:
            self.listen_port = int(netloc[1])
        else:
            if result.scheme == 'http':
                self.listen_port = 80
            elif result.scheme == 'https':
                self.listen_port = 443


    def read_configuration(self):
        config = configparser.ConfigParser()
        config.read([path.expanduser(path.expandvars('~/.oauth-cli.ini')), '.oauth-cli.ini'])

        for attribute in ['saml_callback_url', 'saml_idp_url', 'listen_address', 'listen_port']:
            setattr(self, attribute, config.get(self.api, attribute, fallback=self.defaults.get(attribute)))
            if attribute == 'listen_port' and not self.listen_port:
                self.determine_listen_port()
            if getattr(self, attribute) is None:
                stderr.write(f'ERROR: property {attribute} not set for api {self.api} in ~/.oauth-cli.ini\n')
                exit(1)

        SAMLAccessTokenCallbackhandler.callback_url = self.saml_callback_url


    def set_saml_response(self, saml_response):
        self.saml_response = saml_response

    def accept_saml_response(self):
        SAMLAccessTokenCallbackhandler.handler = (lambda r : self.set_saml_response(r))
        httpd = HTTPServer((self.listen_address, self.listen_port), SAMLAccessTokenCallbackhandler)
        httpd.handle_request()
        httpd.server_close()

    def request_authorization(self):
        params = {
            'redirect_uri': self.saml_callback_url,
        }
        query_parameters = urlencode(params)
        url = f'{self.saml_idp_url}?{query_parameters}'
        webbrowser.open(url)
        self.accept_saml_response()

    def run(self):
        self.read_configuration()
        self.request_authorization()
        if self.saml_response:
            with open(self.saml_response_file, 'w') as f:
                logging.info(f'SAML response stored in {self.saml_response_file}')
                f.write(self.saml_response)
            chmod(self.saml_response_file, 0o600)
        else:
            logging.error('no SAML response retrieved')
            exit(1)
