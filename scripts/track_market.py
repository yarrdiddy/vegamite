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

args = parser.parse_args()

def main():
	symbol = args.symbol
	exchange = args.exchange.upper()

	database = Database()
	session = database.get_session()

	market_object = session.query(Market).filter_by( 
        exchange_code=exchange.upper(), 
        symbol=symbol
	).first()

	market_object.track_data = 'T'

	session.commit()
	session.close()



if __name__ == '__main__':
    main()