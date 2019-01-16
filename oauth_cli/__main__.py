import logging
from sys import exit

import click

from oauth_cli.config import setting
from oauth_cli.pkce import get_access_token, get_id_token
from oauth_cli.saml import get_saml_token
from oauth_cli.aws import assume_role_with_saml


def myfatal(msg, *args, **kwargs):
    """
    override logging fatal, with an error message and exit
    """
    logging.error(msg, *args, **kwargs)
    exit(1)


@click.group(name='oauth-cli', help="""
A command line utility to obtain JWT, SAML tokens and AWS credentials using SAML.
""")
@click.option('--verbose', is_flag=True, default=False, help=' for tracing purposes')
@click.option('--configuration', '-c', default="DEFAULT", help='configured in .oauth-cli.ini to use')
def cli(verbose, configuration):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if verbose else logging.INFO))
    logging.fatal = myfatal
    setting.SECTION = configuration
    if not setting.exists:
        logging.fatal('no configuration %s found in .oauth-cli.ini', configuration)


cli.add_command(get_access_token)
cli.add_command(get_id_token)
cli.add_command(get_saml_token)
cli.add_command(assume_role_with_saml)

if __name__ == '__main__':
    cli()
