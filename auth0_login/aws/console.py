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
import webbrowser

import requests
from boto3 import Session
from botocore.credentials import ReadOnlyCredentials

from auth0_login import fatal, setting


@click.command('aws-console', help='open AWS console from profile')
@click.option('--profile', required=True, help='to store the credentials under')
def open_aws_console(profile: str):
    """
    opens the AWS console for the specified profile.
    """
    c: ReadOnlyCredentials = Session(profile_name=profile).get_credentials().get_frozen_credentials()
    if not c.token:
        fatal('cannot generated a console signin URL from credentials without a session token')

    creds = {'sessionId': c.access_key, 'sessionKey': c.secret_key, 'sessionToken': c.token}
    response = requests.get("https://signin.aws.amazon.com/federation",
                            params={'Action': 'getSigninToken', 'SessionDuration': setting.ROLE_DURATION,
                                    'Session': json.dumps(creds)})
    if response.status_code != 200:
        fatal("could not generate Console signin URL, %s", response.status_code)

    signin_token = response.json()['SigninToken']
    params = {'Action': 'login', 'Issuer': 'awslogin', 'Destination': 'https://console.aws.amazon.com/',
              'SigninToken': signin_token}
    console = requests.Request('GET', 'https://signin.aws.amazon.com/federation', params=params)
    prepared_link = console.prepare()
    webbrowser.open(prepared_link.url, new=1)
