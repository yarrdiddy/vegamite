# To-Do List

## Build/Deploy/Document

* Default configuration file
* Deploy script - or figure out how to properly deploy via docker etc.
* Start writing documentation
* Learn more about what the setup.py script is doing
* Better way of managing versioning - probably one single standalone file
	* Maybe look at that bumpversion thingy

* Ansible steps: DONE
	* Create a user/role for the app
	* Create a home directory: /app/vegamite
	* Clone git into home directory
	* User/role/home for docker
	* Install docker
	* Set up volumes for databases
	* MySQL, docker container, config and volume
	* InfluxDB, docker container, config and volume
	* Redis container, config
	* Create virtualenv for vegamite and activate
	* Python dependencies - requirements.txt
	* Build and deploy vegamite in virtualenv
	* Daemonize celery and run

Ansible modes:
* Provision new instance
	* Set up users
	* Install dependencies
	* Docker images
	* Git pull install etc
	* Initialize database
	* Start worker
* Deploy new version of app
	* Stop worker
	* Git pull
	* Install
	* Start worker


## Codebase

* Database and data layer
* Websockets for realtime data
* Error handling and logging
* Build API endpoints using flask
* Bundle everything in docker container
* Organize tasks back into tasks module.


## Data

* Determine data layer architecture - DONE
* Data model - As needed
* Data flow design
* Database: MySQL container setup, external volume - DONE
* Database: Base data, tracking table - DONE
* Connection pool for all databases
	* MySQL
	* InfluxDB
	* Redis?
* Cache tracked markets, periodically updating the cache on its own schedule.
	* Cache fall-through when checking.


## Test coverage

* Sure up existing test cases
* Write more test cases