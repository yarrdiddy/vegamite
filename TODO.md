# To-Do List

## Build/Deploy/Document

* Start writing documentation
* Learn more about what the setup.py script is doing
* Better way of managing versioning - probably one single standalone file
	* Maybe look at that bumpversion thingy


## Codebase

* Database and data layer - DONE (ish)
	* Need to formalize database conventions - table names and users
	* Database configuration and tuning
* Websockets for realtime data
* Bundle everything in docker container
* Organize tasks back into tasks module. DONE
* Logs should quiet down
* Logs should be rotated
* Externalize celery beat schedule - DONE, well enough
* Instantiate singletons per worker init.


## Data

* Determine data layer architecture - DONE
* Data model - As needed
* Data flow design - Mostly DONE
* Database: MySQL container setup, external volume - DONE
* Database: Base data, tracking table - DONE
* Connection pool for all databases - DONE / default / singletons
	* MySQL - Now implemented as singleton, has its own pool.
	* InfluxDB - Now a singleton, has its own pool.
* Cache tracked markets, periodically updating the cache on its own schedule.
	* Cache fall-through when checking.
	* For now, just readin from mysql, very little cost.

Data to store:
* Trade data - constantly. Periodically downsample.
* Trend data (ohlcv) - constantly.
	* Multiple resolutions: 


## Analytics

* Most basic analytics will be covered by pandas, so we can use these directly
* Build out flask-based generic data service in grafana
	* /
	* search/
	* query/
	* annotations/
* 


## Test coverage

* Sure up existing test cases
* Write more test cases
* WRITE TESTS!!!

