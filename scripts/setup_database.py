from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from influxdb import InfluxDBClient

from vegamite.config import config
from vegamite.model import Market

config_dict = {
	'user': config.database.user,
	'password': config.database.password,
	'host': config.database.host,
	'port': config.database.port
}

DB_CONNECTION = "mysql://{user}:{password}@{host}:{port}/{database}"

DB_CONNECTION_DEFAULT = (DB_CONNECTION.format(
    database='mysql',
    **config_dict))

default_engine = create_engine(DB_CONNECTION_DEFAULT)

def create_database():
	connection = default_engine.connect()
	connection.execute("COMMIT")
	connection.execute("CREATE DATABASE %s" % config.database.name)
	connection.close()
	# TODO: Also set up a default user account

def create_tables():
	new_engine = create_engine(
		DB_CONNECTION.format(
    		database=config.database.name,
    		**config_dict)
    )
	Markets.__table__.create(new_engine)


def reset_database():
	# import ipdb; ipdb.set_trace()
	connection = default_engine.connect()
	connection.execute("COMMIT")
	connection.execute("DROP DATABASE IF EXISTS %s" % config.database.name)
	connection.close()

def create_influx():
	client = InfluxDBClient(host=config.influx.host, port=config.influx.port, username=config.influx.user, password=config.influx.password)
	client.create_database(config.influx.name)
	client.close()


if __name__ == '__main__':
	reset_database()
	create_database()
	create_tables()
	create_influx()
	