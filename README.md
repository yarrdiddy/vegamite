## Vegamite

A small crypto trading platform designed to track analyse, and eventually book trades algorithmically. Vegamite is a python based application using celery to execute a number of scheduled tasks, storing results in an InfluxDB database.

Just a fun project to play around with some new toys and keep myself coding.

## Quickstart

Everything can be provisioned and deployed via the ansibles playbooks in the deployment section. You will need to provide a host location and your own private key in order to make it run.

Target host addresses can be found in /deployment/hosts.

You will need to provide your own github private key, located in /deployment/vars/git_private_key.yaml

Example provisioning and deployment:

    $ ansible-playbook provision.yaml --private-key=~/.ssh/YOUR_PRIVATE_KEY.pem -v --vault-password-file ~/.your_local_password_file.txt

To do a plain deploy just run the deploy.yaml playbook instead.

## Manual quickstart

Vegamite depends on InfluxDB, MySQL and redis, so these dependencies will need to be set up and configured. We'll assume that these are up and running.

To configure, simply set up the configurations for each in /settings.yaml.

To deploy, create a python 3 virtualenv and run:
    $ pip install --upgrade .
from the root directory.

To start, simply start the celery, and celerybeat workers, eg:
    $ celery -A vegamite.tasks worker -B --loglevel=info

Alternatively a celeryd configuration template is included in the deployment directory.



