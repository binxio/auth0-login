import logging

import click

from auth0_login import fatal
from auth0_login.config import setting
from auth0_login.pkce import get_access_token, get_id_token


@click.group(name='pkce-login', help="A command line utility to obtain JWT tokens.")
@click.option('--verbose', is_flag=True, default=False, help=' for tracing purposes')
@click.option('--configuration', '-c', default="DEFAULT", help='configured in .pcke-login to use')
def cli(verbose, configuration):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if verbose else logging.INFO))
    setting.filename = '.pkce-login'
    setting.SECTION = configuration
    if not setting.exists:
        fatal('no configuration %s found in .pcke-login', configuration)


cli.add_command(get_access_token)
cli.add_command(get_id_token)

if __name__ == '__main__':
    cli()
