import requests

from vegamite.API import products, GDAXRequestAuth
from vegamite.config import settings


api_base = 'https://api-public.sandbox.gdax.com'

def test_gdax_response():
	print(products(api_base))


def test_config():
	print(settings)


def test_gdax_request_string():
	# import ipdb; ipdb.set_trace()
	api_key = settings['gdax']['api_key']
	secret_key = settings['gdax']['secret_key']
	passphrase = settings['gdax']['passphrase']

	# auth = GDAXRequestAuth()
	auth = GDAXRequestAuth(api_key, secret_key, passphrase)