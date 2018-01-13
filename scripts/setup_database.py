import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from influxdb import InfluxDBClient

from vegamite.config import config
from vegamite.model import Market
from vegamite.data import MarketData

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
    Market.__table__.create(new_engine)


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


def default_market_data():
    engine = create_engine(
        DB_CONNECTION.format(
            database=config.database.name,
            **config_dict)
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    # Just set up gdax for now
    market_data = MarketData('gdax')
    markets = market_data.exchange.fetch_markets()

    for market in markets:
        print('Adding market %s' % market)
        market_object = Market(
            ccxt_market_id=market.get('id'),
            exchange_code=market_data.exchange.name,
            symbol=market.get('symbol'),
            base_currency=market.get('base'),
            quote_currency=market.get('quote'),
            track_data='T',
            trade_market='F',
            last_updated=datetime.datetime.today()
        )
        session.add(market_object)
    session.commit()
    session.close()


if __name__ == '__main__':
    reset_database()
    create_database()
    create_tables()
    # create_influx()
    default_market_data()
