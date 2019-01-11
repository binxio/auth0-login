import click
import oauth_cli
import logging
from oauth_cli.pkce.command import PKCEGetAccessTokenCommand, PKCEGetIdTokenCommand
from oauth_cli.saml.command import SAMLGetAccessTokenCommand
from oauth_cli.config import setting


@click.group(name='oauth-cli')
@click.option('--verbose', is_flag=True, default=False, help=' for tracing purposes')
@click.option('--configuration', '-c', default="DEFAULT", help='in ~/.oauth-cli.ini to use to obtain the tokens')
def cli(verbose, configuration):
    logging.basicConfig(level=(logging.DEBUG if verbose else logging.INFO))
    setting.SECTION = configuration
    print(setting.SECTION)
    print(setting.CLIENT_ID)


@cli.command('get-access-token')
@click.option('--audience', '-a', help='to obtain an access token for')
def get_access_token(audience):
    cmd = PKCEGetAccessTokenCommand()
    if audience:
        cmd.audience = audience
    cmd.run()

@cli.command('get-id-token')
def get_access_token():
    cmd = PKCEGetIdTokenCommand()
    cmd.run()

@cli.command('get-saml-token')
def get_access_token():
    cmd = SAMLGetAccessTokenCommand()
    cmd.run()


if __name__ == '__main__':
    cli()
