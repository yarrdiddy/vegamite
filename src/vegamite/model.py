from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('mysql://root:mypassword@0.0.0.0:6603/mysql', echo=True)

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	name = Column(String(32))
	fullname = Column(String(32))
	password = Column(String(32))

	def __repr__(self):
		return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)


class Exchange(Base):
	__tablename__ = 'exchange'

	exchange_id = Column(Integer, primary_key=True)


class Market(Base):
	__tablename__ = 'market'

	market_id = Column(Integer, primary_key=True) #smallint not null auto_increment,
	ccxt_market_id = Column(String(50)) # varchar(50) not null,
	exchange_code = Column(String(50)) # varchar(50) not null,
	symbol = Column(String(50)) # varchar(20) not null,
	base_currency = Column(String(50)) # smallint,
	quote_currency = Column(String(50)) # smallint,
	track_data = Column(String(1))
	trade_market = Column(String(1))
	last_updated = Column(DateTime) # datetime,
	backtest_market = Column(String(1))
	
	def __repr__(self):
		return """<Markets(
			market_id='%s', 
			ccxt_market_id='%s', 
			exchange_code='%s',
			symbol='%s',
			base_currency='%s',
			quote_currency='%s',
			track_data=%s,
			trade_market=%s,
			last_updated='%s',
			backtest_market='%s'
		)>""" % (
			self.market_id, 
			self.ccxt_market_id,
			self.exchange_code,
			self.symbol,
			self.base_currency,
			self.quote_currency,
			self.track_data,
			self.trade_market,
			self.last_updated,
			self.backtest_market
		)



