#
# Copyright 2019 - binx.io B.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webbrowser
from http.server import HTTPServer

import click

from auth0_login import fatal, setting
from auth0_login.saml.callback import SAMLAccessTokenCallbackHandler
from auth0_login.util import assert_listen_port_is_available, get_listen_port_from_url


class SAMLGetAccessTokenCommand(object):
    """
    gets a SAML response token from the SAML Provider and prints
    it to standard output.

    The request is sent to `{idp_url}/samlp/{client_id}`. The callback
    is `http://localhost:{listen_port}/saml`.

    you can configure the `listen_port`, `idp_url` and
    `client_id` in the configuration file.
    """

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
        webbrowser.open(self.saml_idp_url)
        self.accept_saml_response()

    def run(self):
        assert_listen_port_is_available(self.listen_port)
        self.request_authorization()
        if self.saml_response:
            print(self.saml_response)
        else:
            fatal('no SAML response retrieved')


@click.command('get-token', help=SAMLGetAccessTokenCommand.__doc__)
def get_saml_token():
    cmd = SAMLGetAccessTokenCommand()
    cmd.run()
