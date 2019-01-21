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
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs


class SAMLAccessTokenCallbackHandler(BaseHTTPRequestHandler):
    @staticmethod
    def handler(response): return print(response)

    def log_message(self, fmt, *args):
        logging.debug("%s - - [%s] %s\n" %
                      (self.client_address[0],
                       self.log_date_time_string(),
                       fmt % args))

    def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(length).decode(self.headers.get('Content-Encoding', 'utf-8'))
        logging.debug('body %s', body)
        try:
            values = parse_qs(body)
        except:
            values = {}

        if 'SAMLResponse' in values:
            SAMLAccessTokenCallbackHandler.handler(''.join(values['SAMLResponse']))
            msg = f'Received SAML response'
        else:
            msg = f'failed to read a SAMLResponse from the post body'

        self.send_response(200)
        self.send_header('Connection', 'close')
        self.send_header('Content-type', 'text/plain;utf-8')
        self.end_headers()
        self.wfile.write(msg.encode('utf-8'))
