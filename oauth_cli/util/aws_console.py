import json
import logging
import sys
import webbrowser

import requests
from boto3 import Session
from botocore.credentials import ReadOnlyCredentials

from oauth_cli.config import setting


def open_aws_console(profile: str):
    """
    opens the AWS console for the specified profile.
    """
    c: ReadOnlyCredentials = Session(profile_name=profile).get_credentials().get_frozen_credentials()
    creds = {'sessionId': c.access_key, 'sessionKey': c.secret_key, 'sessionToken': c.token}
    response = requests.get("https://signin.aws.amazon.com/federation",
                            params={'Action': 'getSigninToken', 'SessionDuration': setting.ROLE_DURATION,
                                    'Session': json.dumps(creds)})
    if response.status_code != 200:
        logging.fatal(response.text)

    signin_token = response.json()['SigninToken']
    params = {'Action': 'login', 'Issuer': 'awslogin', 'Destination': 'https://console.aws.amazon.com/',
              'SigninToken': signin_token}
    console = requests.Request('GET', 'https://signin.aws.amazon.com/federation', params=params)
    prepared_link = console.prepare()
    webbrowser.open(prepared_link.url)


