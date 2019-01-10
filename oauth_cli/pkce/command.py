import json
import configparser
import hashlib
import webbrowser
from base64 import urlsafe_b64encode
from http.server import HTTPServer
from os import path
from random import getrandbits
from sys import exit, stderr, stdout
from urllib.parse import urlencode, urlparse
from uuid import uuid4

from oauth_cli.pkce.callback import PKCEAccessTokenCallbackhandler


class PKCEGetAccessTokenCommand(object):
    def __init__(self):
        self.api = "DEFAULT"
        self.client_id = None
        self.callback_url = None
        self.token_url = None
        self.authorize_url = None
        self.audience = None
        self.scope = None
        self.generate_verifier = None
        self.listen_address = None
        self.listen_port = None
        self.defaults = {'scope': 'profile',
                         'listen_address': '0.0.0.0',
                         'generate_verifier': False}
        self.verifier = "EYOYp0s4oatPC8GwiiQnLP6XFbbvncBGq-VDp8Zk2Xw"
        self.challenge = "DdxpBsQJdFNxBd18fOWi56wft8TNDcYEWNjEX8FiEQY"
        self.tokens = {}


    def determine_listen_port(self):
        result = urlparse(self.callback_url)
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

        for attribute in ['client_id', 'callback_url', 'token_url', 'authorize_url', 'audience', 'scope', 'listen_address', 'listen_port', 'generate_verifier']:
            setattr(self, attribute, config.get(self.api, attribute, fallback=self.defaults.get(attribute)))
            if attribute == 'listen_port' and not self.listen_port:
                self.determine_listen_port()
            if getattr(self, attribute) is None:
                stderr.write(f'ERROR: property {attribute} not set for api {self.api} in ~/.oauth-cli.ini\n')
                exit(1)

        if self.generate_verifier:
            self.generate_code_verifier()

        PKCEAccessTokenCallbackhandler.client_id = self.client_id
        PKCEAccessTokenCallbackhandler.token_url = self.token_url
        PKCEAccessTokenCallbackhandler.callback_url = self.callback_url
        PKCEAccessTokenCallbackhandler.verifier = self.verifier

    def generate_code_verifier(self):
        verifier = bytearray(getrandbits(8) for _ in range(32))
        challenge = hashlib.sha256(verifier).digest()
        self.verifier = self.b64encode(verifier)
        self.challenge = self.b64encode(challenge)

    @staticmethod
    def b64encode(s):
        return urlsafe_b64encode(s).decode('ascii').strip("=")


    def set_tokens(self, tokens):
        self.tokens = tokens

    def accept_access_code(self):
        PKCEAccessTokenCallbackhandler.state = self.state
        PKCEAccessTokenCallbackhandler.handler = (lambda tokens : self.set_tokens(tokens))
        httpd = HTTPServer((self.listen_address, self.listen_port), PKCEAccessTokenCallbackhandler)
        httpd.handle_request()
        httpd.server_close()

    def request_authorization(self):
        self.state = str(uuid4())
        params = {
            "audience": self.audience,
            "scope": self.scope,
            "response_type": "code",
            "client_id": self.client_id,
            "code_challenge": self.challenge,
            "code_challenge_method": "S256",
            "redirect_uri": self.callback_url,
            "state": self.state
        }
        query_parameters = urlencode(params)
        url = f'{self.authorize_url}?{query_parameters}'
        webbrowser.open(url)
        self.accept_access_code()

    def run(self):
        self.read_configuration()
        self.request_authorization()
        if self.tokens:
            json.dump(self.tokens, stdout)
        else:
            logging.error('no token retrieved')
            exit(1)
