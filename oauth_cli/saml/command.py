import logging
import webbrowser
from http.server import HTTPServer
from sys import exit
from urllib.parse import urlencode

import click

from oauth_cli.config import setting
from oauth_cli.saml.callback import SAMLAccessTokenCallbackHandler
from oauth_cli.util import get_listen_port_from_url


class SAMLGetAccessTokenCommand(object):
    def __init__(self):
        self.idp_url = setting.IDP_URL
        self.client_id = setting.CLIENT_ID
        self.tokens = {}
        self.saml_response = None

    @property
    def saml_idp_url(self):
        return f'{self.idp_url}/samlp/{self.client_id}'

    @property
    def callback_url(self):
        return f'http://localhost:{setting.LISTEN_PORT}/saml'

    @property
    def listen_port(self):
        return get_listen_port_from_url(self.callback_url)

    def set_saml_response(self, saml_response):
        self.saml_response = saml_response

    def accept_saml_response(self):
        SAMLAccessTokenCallbackHandler.callback_url = self.callback_url
        SAMLAccessTokenCallbackHandler.handler = (lambda r: self.set_saml_response(r))
        httpd = HTTPServer(('0.0.0.0', self.listen_port), SAMLAccessTokenCallbackHandler)
        httpd.handle_request()
        httpd.server_close()

    def request_authorization(self):
        query_parameters = urlencode({'redirect_uri': self.callback_url})
        webbrowser.open(f'{self.saml_idp_url}?{query_parameters}')
        self.accept_saml_response()

    def run(self):
        self.request_authorization()
        if self.saml_response:
            print(self.saml_response)
        else:
            logging.error('no SAML response retrieved')
            exit(1)


@click.command('get-saml-token', help='get a SAML response token')
def get_saml_token():
    cmd = SAMLGetAccessTokenCommand()
    cmd.run()

