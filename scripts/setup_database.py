import datetime
import argparse

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from influxdb import InfluxDBClient

from vegamite.config import config
from vegamite.model import Market
from vegamite.data import MarketData

# Modes: 
# - Reset/clean databases.
# - Initialize markets, supply a list
# - Track markets?

parser = argparse.ArgumentParser()

parser.add_argument('-r', '--reset', help='Reset databases. Warning: This will delete all data!',  action='store_true')
parser.add_argument('-c', '--create', help="Create databases if they don't exist.",  action='store_true')
parser.add_argument('-t', '--tables', help="Create tables if they don't exist",  action='store_true')
parser.add_argument('-e', '--exchange', help='Initial list of exchanges to enter.', nargs='+')

args = parser.parse_args()


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
    connection.execute("CREATE DATABASE IF NOT EXISTS %s" % config.database.name)
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


def default_market_data(*exchanges):
    engine = create_engine(
        DB_CONNECTION.format(
            database=config.database.name,
            **config_dict)
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    # import ipdb; ipdb.set_trace()
    for exchange in exchanges:
        market_data = MarketData(exchange)
        markets = market_data.exchange.fetch_markets()

        for market in markets:
            market_object = session.query(Market).filter_by(
                ccxt_market_id=market.get('id'), 
                exchange_code=market_data.exchange.name, 
                symbol=market.get('symbol')).first()
            if market_object:
                print('Market: %s, %s exists' % (exchange, market.get('symbol')))
            else:
                print('Adding market %s' % market)
                market_object = Market(
                    ccxt_market_id=market.get('id'),
                    exchange_code=market_data.exchange.name,
                    symbol=market.get('symbol'),
                    base_currency=market.get('base'),
                    quote_currency=market.get('quote'),
                    track_data='F',
                    trade_market='F',
                    last_updated=datetime.datetime.today()
                )
                session.add(market_object)
    session.commit()
    session.close()

def main():
    
    _create_database = args.create
    _create_tables = args.tables
    _exchanges = args.exchange
    _reset = args.reset

    if _reset:
        print('Resetting databases')
        reset_database()

    if _create_database:
        print('Creating databases')
        create_database()
        create_influx()

    if _create_tables:
        print('Creating tables')
        create_tables()

    if _exchanges is not None:
        print('Writing exchanges')
        default_market_data(*_exchanges)


if __name__ == '__main__':
    main()
