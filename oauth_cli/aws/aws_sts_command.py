from sys import stdout

import click

from oauth_cli import fatal, setting
from oauth_cli.aws.aws_account import aws_accounts
from oauth_cli.aws.aws_console import open_aws_console
from oauth_cli.aws.aws_saml_assertion import AWSSAMLAssertion
from oauth_cli.saml import SAMLGetAccessTokenCommand


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
        if not account and self.account:
            self.account = aws_accounts.get_account(self.account).number

        self.role = role if role else setting.attributes.get('aws_role')
        self.profile = profile if profile else setting.attributes.get('aws_profile')
        self.open_console = setting.attributes.get('aws_console', False)
        self.saml_response: AWSSAMLAssertion = None

    def set_saml_response(self, saml_response):
        self.saml_response = AWSSAMLAssertion(saml_response)

    def print_roles(self):
        for role in self.saml_response.available_roles():
            account = aws_accounts.get_account(role.account)
            stdout.write(f'[{role.name}@{account.alias}]\n')
            stdout.write(f'idp_url = {setting.IDP_URL}\n')
            stdout.write(f'client_id = {setting.CLIENT_ID}\n')
            stdout.write(f'aws_account = {account.alias}\n')
            stdout.write(f'aws_role = {role.name}\n')
            stdout.write(f'aws_profile = {role.name}@{account.alias}\n\n')

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
            fatal('--account, --role and --profile are required.')


@click.command('aws-assume-role', help=AWSSTSGetCredentialsFromSAMLCommand.__doc__)
@click.option('--account', help='aws account number or alias')
@click.option('--role', help='to assume using the token')
@click.option('--profile', help='to store the credentials under')
@click.option('--show', is_flag=True, default=False, help='account roles available to assume')
@click.option('--open-console', '-C', count=True, help=' after credential refresh')
def assume_role_with_saml(account, role, profile, show, open_console):

    aws_account = aws_accounts.get_account(account).number if account else None
    cmd = AWSSTSGetCredentialsFromSAMLCommand(aws_account, role, profile)
    if show:
        cmd.show_account_roles()
    else:
        if open_console:
            cmd.open_console = True
        cmd.run()
