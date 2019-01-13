import logging
import socket
from sys import exit

import click

from oauth_cli.config import setting
from oauth_cli.pkce import get_access_token, get_id_token
from oauth_cli.saml import assume_role_with_saml, get_saml_token


def assert_listen_port_is_available():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', setting.LISTEN_PORT))
        s.close()
    except socket.error as e:
        logging.error('port %d is not available, %s', setting.LISTEN_PORT, e.strerror)
        exit(1)


@click.group(name='oauth-cli')
@click.option('--verbose', is_flag=True, default=False, help=' for tracing purposes')
@click.option('--configuration', '-c', default="DEFAULT", help='configured in ~/.oauth-cli.ini to use')
def cli(verbose, configuration):
    logging.basicConfig(level=(logging.DEBUG if verbose else logging.INFO))
    setting.SECTION = configuration
    assert_listen_port_is_available()


cli.add_command(get_access_token)
cli.add_command(get_id_token)
cli.add_command(get_saml_token)
cli.add_command(assume_role_with_saml)

if __name__ == '__main__':
    cli()
