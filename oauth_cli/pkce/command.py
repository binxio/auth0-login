import hashlib
import json
import logging
import webbrowser
from base64 import urlsafe_b64encode
from http.server import HTTPServer
from random import getrandbits
from sys import exit, stdout
from urllib.parse import urlencode
from uuid import uuid4

from oauth_cli.config import setting
from oauth_cli.pkce.callback import PKCEAccessTokenCallbackhandler


class PKCEGetIdTokenCommand(object):
    def __init__(self):
        self.client_id = setting.CLIENT_ID
        self.scope = 'profile'
        self.tokens = {}
        self.state = str(uuid4())

        # TODO: bug report -> Auth0 does not accept any generated verifier/challenge.
        self.generate_verifier = False
        self.verifier = "EYOYp0s4oatPC8GwiiQnLP6XFbbvncBGq-VDp8Zk2Xw"
        self.challenge = "DdxpBsQJdFNxBd18fOWi56wft8TNDcYEWNjEX8FiEQY"

    @property
    def callback_url(self):
        return f'http://localhost:{setting.LISTEN_PORT}/callback'

    @property
    def token_url(self):
        return f'{setting.IDP_URL}/oauth/token'

    @property
    def authorize_url(self):
        return f'{setting.IDP_URL}/authorize'

    def set_tokens(self, tokens):
        self.tokens = tokens

    def accept_access_code(self):
        PKCEAccessTokenCallbackhandler.client_id = setting.CLIENT_ID
        PKCEAccessTokenCallbackhandler.token_url = self.token_url
        PKCEAccessTokenCallbackhandler.callback_url = self.callback_url
        PKCEAccessTokenCallbackhandler.verifier = self.verifier
        PKCEAccessTokenCallbackhandler.state = self.state
        PKCEAccessTokenCallbackhandler.handler = (lambda tokens: self.set_tokens(tokens))
        httpd = HTTPServer(('0.0.0.0', setting.LISTEN_PORT), PKCEAccessTokenCallbackhandler)
        httpd.handle_request()
        httpd.server_close()

    @property
    def query_parameters(self):
        return {
            "response_type": "code",
            "scope": self.scope,
            "client_id": self.client_id,
            "code_challenge": self.challenge,
            "code_challenge_method": "S256",
            "redirect_uri": self.callback_url,
            "state": self.state
        }

    @property
    def url(self):
        return self.authorize_url + '?' + urlencode(self.query_parameters);

    def request_authorization(self):
        webbrowser.open(self.url)
        self.accept_access_code()

    @staticmethod
    def b64encode(s):
        return urlsafe_b64encode(s).decode('ascii').strip("=")

    def generate_code_verifier(self):
        verifier = bytearray(getrandbits(8) for _ in range(32))
        challenge = hashlib.sha256(verifier).digest()
        self.verifier = self.b64encode(verifier)
        self.challenge = self.b64encode(challenge)

    def run(self):
        self.request_authorization()
        if self.tokens:
            json.dump(self.tokens, stdout)
        else:
            logging.error('no token retrieved')
            exit(1)


class PKCEGetAccessTokenCommand(PKCEGetIdTokenCommand):
    def __init__(self):
        super(PKCEGetAccessTokenCommand,self).__init__()
        self.audience = setting.attributes.get('audience')

    @property
    def query_parameters(self):
        result = super(PKCEGetAccessTokenCommand,self).query_parameters
        result.update({"audience": self.audience })
        return result


    def run(self):
        if not self.audience:
            logging.error('audience is required')
            exit(1)
        super(PKCEGetAccessTokenCommand,self).run()
