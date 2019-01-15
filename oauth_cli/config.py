from os import path
import logging
import configparser


class __Setting(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read([path.expanduser(path.expandvars('~/.oauth-cli.ini')), '.oauth-cli.ini'])
        self.__SECTION = 'DEFAULT'

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
            logging.fatal('property client_id is missing from .oauth-cli.ini')
        return self.config.get(self.SECTION, 'client_id')

    @property
    def IDP_URL(self):
        if not self.config.has_option(self.SECTION, 'idp_url'):
            logging.fatal('property idl_url is missing from .oauth-cli.ini')
        return self.config.get(self.SECTION, 'idp_url')

    @property
    def exists(self):
        return self.config.has_section(self.SECTION)


setting = __Setting()
