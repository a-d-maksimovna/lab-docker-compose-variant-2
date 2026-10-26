import os
from decimal import Decimal
import psycopg2
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
DB = os.environ['DATABASE_URL']
SERVICE = os.environ['WEB_SERVICE_URL']

@app.get('/api/history')
def history():
    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, amount, source_currency, target_currency, result, rate, created_at FROM conversions ORDER BY id DESC LIMIT 30')
            rows = cur.fetchall()
    return jsonify([dict(id=r[0], amount=float(r[1]), source=r[2], target=r[3], result=float(r[4]), rate=float(r[5]), created_at=r[6].isoformat()) for r in rows])

@app.post('/api/convert')
def convert():
    data = request.get_json(silent=True) or {}
    try:
        amount = Decimal(str(data['amount']))
        source = str(data['source']).upper()
        target = str(data['target']).upper()
        if not amount.is_finite() or amount <= 0 or amount > 1000000000:
            raise ValueError('Сумма должна быть больше 0 и не более 1 млрд')
        if source not in ('USD','EUR','RUB','GBP','CNY') or target not in ('USD','EUR','RUB','GBP','CNY'):
            raise ValueError('Неизвестная валюта')
    except (KeyError, ValueError, TypeError, ArithmeticError) as exc:
        return jsonify(error=str(exc)), 400
    try:
        response = requests.get(f'{SERVICE}/rate', params={'source': source, 'target': target}, timeout=8)
        response.raise_for_status()
        rate = Decimal(str(response.json()['rate']))
        result = (amount * rate).quantize(Decimal('0.0001'))
        with psycopg2.connect(DB) as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO conversions (amount,source_currency,target_currency,result,rate) VALUES (%s,%s,%s,%s,%s)', (amount,source,target,result,rate))
        return jsonify(amount=float(amount), source=source, target=target, rate=float(rate), result=float(result))
    except (requests.RequestException, psycopg2.Error, ValueError) as exc:
        return jsonify(error=f'Ошибка сервиса: {exc}'), 503

app.run(host='0.0.0.0', port=5000)
