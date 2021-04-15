import requests
import json

def get_response():
	r = requests.get('https://api.binance.com/api/v3/ticker/price')

	if r.status_code == 200:
		response = r.json()
	else:
		response = None
	return response

def make_easy_dict(response):
	# making dict pair:price
	pairs_dict = {}
	for pair in response:
		pairs_dict[pair['symbol']] = pair['price']

	return pairs_dict

def write_json_file(filename, dict_tumbler=None):

	if dict_tumbler:
		pairs_dict = dict_tumbler
	else:
		response = get_response()
		if response:
			pairs_dict = make_easy_dict(response)

	try:
		with open(filename, 'w') as file:
			json.dump(pairs_dict, file)
	except Exception:
		pass

async def read_json_file(filename):
	with open(filename, 'r') as file:
		try:
			pairs_dict = json.load(file)
		except Exception:
			pairs_dict = None
	
	return pairs_dict