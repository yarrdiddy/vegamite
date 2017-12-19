import requests

def products(api_base):
	response = requests.get(api_base + '/products')

	# Check for invalid response
	if response.status_code is not 200:
		raise Exception('Invalid GDAX Status Code: %d' % response.status_code)

	return response.json()