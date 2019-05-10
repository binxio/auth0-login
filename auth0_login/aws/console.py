#
# Copyright 2019 - binx.io B.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import click
import logging
import webbrowser

import requests
from boto3 import Session
from botocore.credentials import ReadOnlyCredentials
from botocore.exceptions import ClientError

from auth0_login import fatal, setting


def get_federated_credentials(session: Session) -> ReadOnlyCredentials:
    iam = session.client('iam')
    sts = session.client('sts')
    policy = {"Version": "2012-10-17", "Statement": [{"Action": "*", "Effect": "Allow", "Resource": "*"}]}
    try:
        user = iam.get_user()
        r = sts.get_federation_token(Name=user['User']['UserName'], DurationSeconds=setting.ROLE_DURATION, Policy=json.dumps(policy))
        c = r['Credentials']
        return ReadOnlyCredentials(access_key=c['AccessKeyId'], secret_key=c['SecretAccessKey'], token=c['SessionToken'])
    except ClientError as e:
        fatal('failed to get federation token, %s', e)

def open_aws_console(profile: str):
    """
    opens the AWS console for the specified profile.
    """
    s: Session = Session(profile_name=profile)
    c: ReadOnlyCredentials = s.get_credentials().get_frozen_credentials()
    if not c.token:
        logging.debug('getting federated credentials')
        c = get_federated_credentials(s)

    if not c.token:
        fatal('cannot generated a console signin URL from credentials without a session token')

    creds = {'sessionId': c.access_key, 'sessionKey': c.secret_key, 'sessionToken': c.token}
    logging.debug('obtaining AWS console signin token')
    response = requests.get("https://signin.aws.amazon.com/federation",
                            params={'Action': 'getSigninToken',
                                    'SessionType': 'json', 'Session': json.dumps(creds)})
    if response.status_code != 200:
        fatal("could not generate Console signin URL, %s,\n%s", response.status_code, response.text)

    signin_token = response.json()['SigninToken']
    params = {'Action': 'login', 'Issuer': 'awslogin', 'Destination': 'https://console.aws.amazon.com/',
              'SigninToken': signin_token}
    logging.debug('opening AWS console')
    console = requests.Request('GET', 'https://signin.aws.amazon.com/federation', params=params)
    prepared_link = console.prepare()
    webbrowser.open(prepared_link.url)


@click.command('aws-console', help='open AWS console from profile')
@click.option('--verbose', is_flag=True, default=False, help=' for tracing purposes')
@click.option('--profile', required=True, help='to store the credentials under')
def main(verbose, profile):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if verbose else logging.INFO))
    open_aws_console(profile)
