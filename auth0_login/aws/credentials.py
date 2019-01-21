import logging
import configparser
from collections import namedtuple
from os import chmod, path

AWSCredentials = namedtuple('AWSCredentials', 'access_key secret_key session_token expiration')


def write_aws_credentials(credentials: AWSCredentials, profile: str):
    filename = path.expanduser(path.expandvars('~/.aws/credentials'))
    config = configparser.ConfigParser()
    config.read(filename)
    if not config.has_section(profile):
        config.add_section(profile)
    config.set(profile, 'aws_access_key_id', credentials.access_key)
    config.set(profile, 'aws_secret_access_key',  credentials.secret_key)
    if credentials.session_token:
        config.set(profile, 'aws_session_token', credentials.session_token)
    else:
        config.remove_option(profile, 'aws_session_token')
    if credentials.expiration:
        config.set(profile, 'expiration', f'credentials.expiration')
    else:
        config.remove_option(profile, 'expiration')
    with open(filename, 'w') as f:
        config.write(f)
    chmod(filename, 0o600)
    logging.info(f'credentials saved under AWS profile {profile}.')
