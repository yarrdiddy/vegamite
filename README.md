## To put in this file:

* A description of your project
* Links to the project's ReadTheDocs page
* A TravisCI button showing the state of the build
* "Quickstart" documentation (how to quickly install and use your project)
* A list of non-Python dependencies (if any) and how to install them

Thanks [https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/](https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

## Docker startup commands:

**MySQL**
docker run --detach --name=test-mysql --env="MYSQL_ROOT_PASSWORD=mypassword" --publish 6603:3306 --volume=/Users/dave/code/root/container/test-mysql/conf.d/:/etc/mysql/conf.d mysql

**InfluxDB**
docker run --name=test-influxdb --detach -p 8086:8086 -v $VEGAMITE_DATA/influxdb:/var/lib/influxdb influxdb

**Redis**
docker run --name=vegamite-redis -p 6379:6379 -d redis

**Useful commands**
docker ps


