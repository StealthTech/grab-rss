import configparser
import os

CONFIG_BASEDIR = 'config'


class Configuration:
    def __init__(self, filename):
        self.filename = filename
        self.fullpath = f'{CONFIG_BASEDIR}/{filename}'
        self.check_exists()

    def make(self, force = False):
        if not os.path.exists(self.fullpath) or force:
            config = configparser.ConfigParser()
            config['PREDEFINED'] = { 'secret_key': '' }

            with open(self.fullpath, 'w') as configfile:
                config.write(configfile)

    def check_exists(self):
        if not os.path.exists(self.fullpath):
            self.make()

    def get(self, section, key):
        self.check_exists()
        config = configparser.ConfigParser()
        config.read(self.fullpath)
        try:
            result = config[section][key]
            return result
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            print(e)

    def set(self, section, key, data):
        self.check_exists()
        config = configparser.ConfigParser()
        config.read(self.fullpath)
        try:
            config[section][key] = data
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            print(e)
