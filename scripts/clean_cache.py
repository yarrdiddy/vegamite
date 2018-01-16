from vegamite.data import redis_client

r = redis_client()

def clear_exchange_locks():
	r.set('lock_gdax', 'false')


if __name__ == '__main__':
	clear_exchange_locks()