import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs


class SAMLAccessTokenCallbackHandler(BaseHTTPRequestHandler):
    handler = lambda response: print(response)

    def log_message(self, format, *args):
        logging.debug("%s - - [%s] %s\n" %
                      (self.client_address[0],
                       self.log_date_time_string(),
                       format % args))

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
