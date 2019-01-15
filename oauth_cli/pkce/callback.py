import json
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import jwt
import requests


class PKCEAccessTokenCallbackHandler(BaseHTTPRequestHandler):
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
        for token in ['id_token', 'access_token']:
            try:
                if '.' in tokens[token]:
                    self.wfile.write(json.dumps(jwt.decode(tokens[token], verify=False), indent=2).encode('utf-8'))
            except jwt.DecodeError as e:
                logging.debug(f'failed to decode {token}, {e}')

    def write_reply(self, msg, loglevel=logging.DEBUG):
        self.send_response(200)
        self.send_header('Connection', 'close')
        self.send_header('Content-type', 'text/plain;utf-8')
        self.end_headers()
        self.wfile.write(msg.encode('utf-8'))
        logging.log(loglevel, msg)
        return

    def do_GET(self):
        codes = parse_qs(urlparse(self.path).query)
        state = ''.join(codes.get('state', []))
        if state != PKCEAccessTokenCallbackHandler.state:
            msg = f'Authentication failed! expected code for state {PKCEAccessTokenCallbackHandler.state}, received {state}.'
            self.write_reply(msg, logging.ERROR)
            return

        if 'error' in codes:
            msg = f'Authentication failed! {codes}'
            self.write_reply(msg, logging.ERROR)
            return

        body = {
            "grant_type": "authorization_code",
            "client_id": PKCEAccessTokenCallbackHandler.client_id,
            "code_verifier": PKCEAccessTokenCallbackHandler.verifier,
            "code": codes['code'][0],
            "redirect_uri": PKCEAccessTokenCallbackHandler.callback_url,
        }
        logging.debug('obtaining access token with code, %s', body)
        response = requests.post(PKCEAccessTokenCallbackHandler.token_url, json=body)
        logging.debug('status code %d, %s', response.status_code, response.text)

        if response.status_code == 200:
            self.write_reply('Authenticated! You may close this window.\n')
            tokens = response.json()
            PKCEAccessTokenCallbackHandler.handler(tokens)
            self.write_tokens(tokens)
        else:
            self.write_reply(f'Authentication failed! {response.text}', logging.ERROR)
