import argparse

from vegamite.config import config
from vegamite.model import Market
from vegamite.data import MarketData, Database

parser = argparse.ArgumentParser()

# parser.add_argument('-r', '--reset', help='Reset databases. Warning: This will delete all data!',  action='store_true')
# parser.add_argument('-c', '--create', help="Create databases if they don't exist.",  action='store_true')
# parser.add_argument('-t', '--tables', help="Create tables if they don't exist",  action='store_true')
# parser.add_argument('-e', '--exchange', help='Initial list of exchanges to enter.', nargs='+')
parser.add_argument('-s', '--symbol', help="Market to track", type=str)
parser.add_argument('-e', '--exchange', help="Exchange to track", type=str)
parser.add_argument('-t', '--track', action='store_true')
parser.add_argument('-S', '--stop', action='store_true')

args = parser.parse_args()

database = Database()

def track_one_market(exchange, symbol):
	session = database.get_session()

	market_object = session.query(Market).filter_by( 
        exchange_code=exchange.upper(), 
        symbol=symbol
	).first()

	market_object.track_data = 'T'

	session.commit()
	session.close()


def track_exchange(exchange):
	session = database.get_session()

	market_query = session.query(Market).filter_by(exchange_code=exchange)

	for market in market_query:
		market.track_data = 'T'

	session.commit()
	session.close()


def stop_tracking_market(exchange, symbol):
	pass


def stop_tracking_exchange(exchange):
	pass


def main():
	_symbol = args.symbol
	_exchange = args.exchange.upper()
	_track = args.track
	_stop = args.stop

	if _track:
		if _symbol is not None and _exchange is not None:
			track_one_market(_exchange, _symbol)
		elif _symbol is None and _exchange is not None:
			track_exchange(_exchange)
	elif _stop:
		if _symbol is not None and _exchange is not None:
			stop_tracking_market(_exchange, _symbol)
		elif _symbol is None and _exchange is not None:
			stop_tracking_exchange(_exchange)


if __name__ == '__main__':
    main()