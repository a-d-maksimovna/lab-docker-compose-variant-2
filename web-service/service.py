from flask import Flask, request, jsonify
import requests
app = Flask(__name__)
@app.get('/rate')
def rate():
    source = request.args.get('source','USD').upper()
    target = request.args.get('target','EUR').upper()
    if source not in ('USD','EUR','RUB','GBP','CNY') or target not in ('USD','EUR','RUB','GBP','CNY'):
        return jsonify(error='Unknown currency'), 400
    if source == target:
        return jsonify(rate=1, source=source, target=target)
    try:
        r = requests.get(f'https://open.er-api.com/v6/latest/{source}', timeout=12)
        r.raise_for_status()
        data = r.json()
        if data.get('result') != 'success':
            raise ValueError('Exchange rate unavailable')
        return jsonify(rate=data['rates'][target], source=source, target=target, updated=data.get('time_last_update_utc'))
    except (requests.RequestException, KeyError, ValueError) as exc:
        return jsonify(error=str(exc)), 503
app.run(host='0.0.0.0', port=5001)
