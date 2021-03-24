import requests
# заменить на реквест с фаст апи, должен быть

def get_response():
	r = requests.get('https://api.binance.com/api/v3/ticker/price')

	if r.status_code == 200:
		response = r.json()
	else:
		response = None

	return response

resp = get_response()
print(len(resp))

for pair in resp:
    if pair.get('symbol') == 'BTCUSDT':
        print(pair.get('symbol'))
        print(pair.get('price'))
