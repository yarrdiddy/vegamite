import yaml
import os

from collections import namedtuple

class Configuration(object):
    def __init__(self, config_file):

        self.app_home = os.environ['VEGAMITE_HOME']

        with open(self.app_home + '/vegamite/' + config_file) as config_file:
            settings = yaml.load(config_file)
            for name in settings.keys():
                self.__dict__.update(settings)

app_home = os.environ['VEGAMITE_HOME']

def convert_to_namedtuple(config_data):
    for key, value in config_data.items():
        if isinstance(value, dict):
            config_data[key] = convert_to_namedtuple(value)
    return namedtuple('ConfigDict', config_data.keys())(*config_data.values())

def parse_configuration(config_file):
    with open(app_home + '/vegamite/' + config_file) as _file:
        settings = yaml.load(_file)
        return convert_to_namedtuple(settings)

config = parse_configuration('settings.yaml')