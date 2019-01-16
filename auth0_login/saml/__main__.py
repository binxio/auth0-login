import logging

import click

from auth0_login import fatal
from auth0_login.aws import assume_role_with_saml
from auth0_login.config import setting
from auth0_login.saml import get_saml_token


@click.group(name='saml-login', help="A command line utility to obtain SAML tokens and AWS credentials.")
@click.option('--verbose', is_flag=True, default=False, help=' for tracing purposes')
@click.option('--configuration', '-c', default="DEFAULT", help='configured in .oauth-cli.ini to use')
def cli(verbose, configuration):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if verbose else logging.INFO))
    setting.filename = '.saml-login'
    setting.SECTION = configuration
    if not setting.exists:
        fatal('no configuration %s found in %s', configuration, setting.filename)


cli.add_command(get_saml_token)
cli.add_command(assume_role_with_saml)

if __name__ == '__main__':
    cli()
