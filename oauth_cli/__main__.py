import logging

import click

from oauth_cli.config import setting
from oauth_cli.pkce import PKCEGetAccessTokenCommand, PKCEGetIdTokenCommand
from oauth_cli.saml import SAMLGetAccessTokenCommand, AWSSTSGetCredentialsFromSAMLCommand


@click.group(name='oauth-cli')
@click.option('--verbose', is_flag=True, default=False, help=' for tracing purposes')
@click.option('--application', default="DEFAULT", help='configured in ~/.oauth-cli.ini to use')
def cli(verbose, application):
    logging.basicConfig(level=(logging.DEBUG if verbose else logging.INFO))
    setting.SECTION = application
    print(setting.SECTION)
    print(setting.CLIENT_ID)


@cli.command('get-access-token')
@click.option('--audience', help='to obtain an access token for. default from ~/.oauth-cli.ini')
@click.option('--scope', default='profile', help='of the access token')
def get_access_token(audience, scope):
    cmd = PKCEGetAccessTokenCommand()
    if audience:
        cmd.audience = audience
    if scope:
        cmd.scope = scope
    cmd.run()

@cli.command('get-id-token')
def get_access_token():
    cmd = PKCEGetIdTokenCommand()
    cmd.run()

@cli.command('get-saml-token')
def get_access_token():
    cmd = SAMLGetAccessTokenCommand()
    cmd.run()

@cli.command('aws-saml-assume-role')
@click.option('--account', help='aws account number')
@click.option('--role', help='to assume using the token')
@click.option('--profile', help='to store the credentials under')
def get_access_token(account, role, profile):
    cmd = AWSSTSGetCredentialsFromSAMLCommand(account, role, profile)
    cmd.run()


if __name__ == '__main__':
    cli()
