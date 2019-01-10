import click
import oauth_cli
import logging
from oauth_cli.pkce.command import PKCEGetAccessTokenCommand
from oauth_cli.saml.command import SAMLGetAccessTokenCommand


@click.group(name='oauth')
@click.option('--verbose', is_flag=True, default=False, help=' for tracing purposes')
def cli(verbose):
    logging.basicConfig(level=(logging.DEBUG if verbose else logging.INFO))


@cli.command('get-access-token')
def get_access_token():
    cmd = PKCEGetAccessTokenCommand()
    cmd.run()


@cli.command('get-saml-token')
def get_access_token():
    cmd = SAMLGetAccessTokenCommand()
    cmd.run()


if __name__ == '__main__':
    cli()
