import logging
import webbrowser
from http.server import HTTPServer
from os import path, chmod
from sys import exit
from urllib.parse import urlencode

from oauth_cli.config import setting
from oauth_cli.saml.callback import SAMLAccessTokenCallbackhandler


class SAMLGetAccessTokenCommand(object):
    def __init__(self):
        self.idp_url = setting.IDP_URL
        self.client_id = setting.CLIENT_ID
        self.saml_response_file = path.expandvars(path.expanduser('~/.aws/saml-response'))
        self.tokens = {}

    @property
    def saml_idp_url(self):
        return f'{self.idp_url}/samlp/{self.client_id}'

    @property
    def callback_url(self):
        return f'http://localhost:{setting.LISTEN_PORT}/saml'

    def set_saml_response(self, saml_response):
        self.saml_response = saml_response

    def accept_saml_response(self):
        SAMLAccessTokenCallbackhandler.callback_url = self.callback_url
        SAMLAccessTokenCallbackhandler.handler = (lambda r: self.set_saml_response(r))
        httpd = HTTPServer(('0.0.0.0', setting.LISTEN_PORT), SAMLAccessTokenCallbackhandler)
        httpd.handle_request()
        httpd.server_close()

    def request_authorization(self):
        params = {
            'redirect_uri': self.callback_url,
        }
        query_parameters = urlencode(params)
        webbrowser.open(f'{self.saml_idp_url}?{query_parameters}')
        self.accept_saml_response()

    def run(self):
        self.request_authorization()
        if self.saml_response:
            with open(self.saml_response_file, 'w') as f:
                logging.info(f'SAML response stored in {self.saml_response_file}')
                f.write(self.saml_response)
            chmod(self.saml_response_file, 0o600)
        else:
            logging.error('no SAML response retrieved')
            exit(1)
