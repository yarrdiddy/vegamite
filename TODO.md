# To-Do List

## Build/Deploy/Document

* Default configuration file
* Deploy script - or figure out how to properly deploy via docker etc.
* Start writing documentation
* Learn more about what the setup.py script is doing
* Better way of managing versioning - probably one single standalone file
	* Maybe look at that bumpversion thingy


## Codebase

* Database and data layer
* Websockets for realtime data
* Error handling and logging
* Build API endpoints using flask
* Wrap flask in gunicorn for async
* Bundle everything in docker container


## Data

* Determine data layer architecture
	* Likely a combination of SQLite with redis and/or a persistent document store
* Data model
* Data flow design


## Test coverage

* Sure up existing test cases
* 