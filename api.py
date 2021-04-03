import requests
import json


def get_response():
	r = requests.get('https://api.binance.com/api/v3/ticker/price')

	if r.status_code == 200:
		response = r.json()
	else:
		response = None
	return response


def write_json_file():
	response = get_response()
	if response:

		# делаем дикт пара:цена для удобства
		pairs_dict = {}
		for pair in response:
			pairs_dict[pair['symbol']] = pair['price']

		try:
			with open('trade_pairs.json', 'w') as file:
				json.dump(pairs_dict, file)
		except Exception:
			pass


async def read_json_file():
	with open('trade_pairs.json', 'r') as file:
		try:
			pairs = json.load(file)
		except Exception:
			pairs = None
	
	return pairs