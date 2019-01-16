import configparser
from os import path

from auth0_login.logging import fatal


class __Setting(object):
    def __init__(self):
        self.filename = '.pcke-login'
        self.__SECTION = 'DEFAULT'

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, filename):
        self.__filename = filename
        self.config = configparser.ConfigParser()
        self.config.read([path.expanduser(path.expandvars(f'~/{filename}')), f'{filename}'])

    @property
    def SECTION(self):
        return self.__SECTION

    @SECTION.setter
    def SECTION(self, section):
        self.__SECTION = section

    @property
    def attributes(self) -> dict:
        return {v[0]: v[1] for v in self.config.items(self.SECTION)}

    @property
    def LISTEN_PORT(self):
        return self.config.getint(self.SECTION, 'listen_port', fallback=12200)

    @property
    def ROLE_DURATION(self):
        return self.config.getint(self.SECTION, 'role_duration', fallback=3600)

    @property
    def CLIENT_ID(self):
        if not self.config.has_option(self.SECTION, 'client_id'):
            fatal(f'property client_id is missing from .{self.filename}')
        return self.config.get(self.SECTION, 'client_id')

    @property
    def IDP_URL(self):
        if not self.config.has_option(self.SECTION, 'idp_url'):
            fatal(f'property client_id is missing from .{self.filename}')
        return self.config.get(self.SECTION, 'idp_url')

    @property
    def exists(self):
        return self.SECTION == 'DEFAULT' or self.config.has_section(self.SECTION)


setting = __Setting()
