from vegamite.data import redis_client

r = redis_client()

def clear_exchange_locks():
	r.delete('lock_gdax')


if __name__ == '__main__':
	clear_exchange_locks()