import click
import oauth_cli
import logging
from oauth_cli.pkce.command import PKCEGetAccessTokenCommand


@click.group(name='oauth')
@click.option('--verbose', is_flag=True, default=False, help=' for tracing purposes')
def cli(verbose):
    logging.basicConfig(level=(logging.DEBUG if verbose else logging.INFO))

@cli.command('get-access-token')
def get_access_token():
    cli = PKCEGetAccessTokenCommand()
    cli.run()

if __name__ == '__main__':
    cli()

