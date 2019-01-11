import json
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import jwt
import requests


class PKCEAccessTokenCallbackhandler(BaseHTTPRequestHandler):
    client_id = None
    verifier = None
    callback_url = None
    token_url = None
    state = None
    handler = lambda tokens: print(tokens.get('access_token'))

    def log_message(self, fmt, *args):
        logging.debug("%s - - [%s] %s\n" %
                      (self.client_address[0],
                       self.log_date_time_string(),
                       fmt % args))

    def write_tokens(self, tokens):
        if 'id_token' in tokens:
            self.wfile.write(json.dumps(jwt.decode(tokens['id_token'], verify=False), indent=2).encode('utf-8'))
        elif 'access_token' in tokens:
            self.wfile.write(json.dumps(jwt.decode(tokens['access_token'], verify=False), indent=2).encode('utf-8'))

    def write_reply(self, msg, loglevel=logging.DEBUG):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain;utf-8')
        self.end_headers()
        self.wfile.write(msg.encode('utf-8'))
        logging.log(loglevel, msg)
        return

    def do_GET(self):
        codes = parse_qs(urlparse(self.path).query)
        state = ''.join(codes.get('state', []))
        if state != PKCEAccessTokenCallbackhandler.state:
            msg = f'Authentication failed! expected code for state {PKCEAccessTokenCallbackhandler.state}, received {state}.'
            self.write_reply(msg, logging.ERROR)
            return

        if 'error' in codes:
            msg = f'Authentication failed! {codes}'
            self.write_reply(msg, logging.ERROR)
            return

        body = {
            "grant_type": "authorization_code",
            "client_id": PKCEAccessTokenCallbackhandler.client_id,
            "code_verifier": PKCEAccessTokenCallbackhandler.verifier,
            "code": codes['code'][0],
            "redirect_uri": PKCEAccessTokenCallbackhandler.callback_url,
            "prompt": "none"
        }
        logging.debug('obtaining access token with code, %s', body)
        response = requests.post(PKCEAccessTokenCallbackhandler.token_url, json=body)
        logging.debug('status code %d, %s', response.status_code, response.text)

        if response.status_code == 200:
            self.write_reply('Authenticated! You may close this window.')
            tokens = response.json()
            PKCEAccessTokenCallbackhandler.handler(tokens)
            self.write_tokens(tokens)
        else:
            self.write_reply(f'Authentication failed! {response.text}', logging.ERROR)
