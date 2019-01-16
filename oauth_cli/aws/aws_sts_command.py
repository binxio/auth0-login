import logging
from sys import stdout

import click

from oauth_cli.aws.aws_console import open_aws_console
from oauth_cli.aws.aws_saml_assertion import AWSSAMLAssertion
from oauth_cli.config import setting
from oauth_cli.saml.command import SAMLGetAccessTokenCommand


class AWSSTSGetCredentialsFromSAMLCommand(SAMLGetAccessTokenCommand):
    """
    get AWS credentials using the obtained SAML token and
    stores then in `~/.aws/credentials`.

    As multiple AWS roles may have been granted to the SAML token,
    the caller has to specify the `account` number and `role` name to
    generate the credentials for. If you are unsure which accounts
    and roles have been granted, use the `--show` option

    The credentials will be stored under the specified `profile` name.
    By specifying `--open-console` it will open the AWS console too.
    """

    def __init__(self, account, role, profile):
        super(AWSSTSGetCredentialsFromSAMLCommand, self).__init__()
        self.account = account if account else setting.attributes.get('aws_account')
        self.role = role if role else setting.attributes.get('aws_role')
        self.profile = profile if profile else setting.attributes.get('aws_profile')
        self.open_console = setting.attributes.get('aws_console', False)
        self.saml_response: AWSSAMLAssertion = None

    def set_saml_response(self, saml_response):
        self.saml_response = AWSSAMLAssertion(saml_response)

    def print_roles(self):
        for role in self.saml_response.available_roles():
            stdout.write(f'oauth-cli ')
            if setting.SECTION != 'DEFAULT':
                stdout.write(f'-c {setting.SECTION} ')
            profile = self.profile if self.profile else f'{role.name}@{role.account}'
            stdout.write(f'aws-saml-assume-role --profile {profile} --acount {role.account} --role {role.name}\n')

    def show_account_roles(self):
        self.request_authorization()
        self.print_roles()

    def run(self):
        if self.account and self.role and self.profile:
            self.request_authorization()
            self.saml_response.assume_role(role_arn=f'arn:aws:iam::{self.account}:role/{self.role}',
                                           profile=self.profile,
                                           duration=setting.ROLE_DURATION)
            if self.open_console:
                open_aws_console(self.profile)
        else:
            logging.fatal('--account, --role and --profile are required.')


@click.command('aws-saml-assume-role', help=AWSSTSGetCredentialsFromSAMLCommand.__doc__)
@click.option('--account', help='aws account number')
@click.option('--role', help='to assume using the token')
@click.option('--profile', help='to store the credentials under')
@click.option('--show', is_flag=True, default=False, help='account roles available to assume')
@click.option('--open-console', '-C', count=True, help=' after credential refresh')
def assume_role_with_saml(account, role, profile, show, open_console):
    cmd = AWSSTSGetCredentialsFromSAMLCommand(account, role, profile)
    if show:
        cmd.show_account_roles()
    else:
        if open_console:
            cmd.open_console = True
        cmd.run()
