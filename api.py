#from io import open_code
import requests
import json

# заменить на реквест с фаст апи, должен быть

def get_response():
	r = requests.get('https://api.binance.com/api/v3/ticker/price')

	if r.status_code == 200:
		response = r.json()
	else:
		response = None
	return response


def write_json_file():

	resp = get_response()
	if resp:

		try:
			with open('tokens.json', 'w') as tokens_file:
				json.dump(resp, tokens_file)
		except Exception:
			pass


async def read_json_file():

	with open('tokens.json', 'r') as tokens_file:
		try:
			tokens = json.load(tokens_file)
		except Exception:
			tokens = None
	
	return tokens