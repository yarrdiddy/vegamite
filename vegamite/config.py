import yaml
import os

app_home = os.environ['VEGAMITE_HOME']

with open(app_home + '/vegamite/settings.yaml') as config_file:
	settings = yaml.load(config_file)