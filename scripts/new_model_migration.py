from influxdb import InfluxDBClient, DataFrameClient

from vegamite.data import TimeSeriesClient
from vegamite.config import config



# Update influxdb a bit
# Going to have four measurements:
#  - trade_data
#      - Will have short retention policy, and several downsample policies to OHLCV format
#  - trend_data
#     - Infinite retention
#     - destination for downsampling of trade data
#  - stats
#     - Short retention, long enough for backtesting
#     - Not yet used
#  - book
#     - For order book data
#     - short retention
#     - not yet used
#
# ==========================
# Migration procedure:
#  - Set retention policies
#  - Create continuous queries
#  - Test everything worked!!


ts = TimeSeriesClient()

def set_policies():
    # "select first(price) as open, max(price) as high, min(price) as low, last(price) as close, sum(amount) as volume from trade_data where exchange='gdax' and symbol = 'BTC/USD' group by time(5m)"
    ts.client.create_retention_policy('90day', '90d', 1, database='vegamite')
    ts.client.create_retention_policy('1year', '52w', 1, database='vegamite')

    ts.client.query("""
        CREATE CONTINUOUS QUERY "raw_trend" ON "vegamite"
        BEGIN
            select  first("price") as open, 
                    max("price") as high, 
                    min("price") as low, 
                    last("price") as close, 
                    sum("amount") as volume 
            into    "90day"."trend"
            from    "90day".trade_data" 
            group by 
                time(5m), "exchange", "symbol"
        END
    """)

def migrate_trade_data():    
    ts.client.query("""
        select  *
        into    "90day"."trade_data"
        from    "trade_data"
    """)

def migrate_trend_data():
    pass

def validate_trade_data():
    pass

def validate_trend_data():
    pass


def main():
    set_policies()
    migrate_trade_data()
    migrate_trend_data()

    validate_trade_data()
    validate_trend_data()

if __name__ == '__main__':
    main()
