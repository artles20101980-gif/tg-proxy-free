# main.py — Прокси к Telegram Bot API для Render
import os
from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)

TELEGRAM_API = "https://api.telegram.org"

@app.route('/bot<token>/<method>', methods=['POST'])
def proxy(token, method):
    """Проксирует POST-запросы к Telegram API"""
    try:
        url = f"{TELEGRAM_API}/bot{token}/{method}"
        
        # Копируем заголовки (кроме hop-by-hop)
        headers = {
            key: value for key, value in request.headers
            if key.lower() not in ['host', 'connection']
        }
        headers['Host'] = 'api.telegram.org'
        
        # Отправляем запрос к Telegram
        resp = requests.post(
            url,
            headers=headers,
            data=request.get_data(),
            timeout=30
        )
        
        # Возвращаем ответ
        return Response(
            resp.content,
            status=resp.status_code,
            content_type='application/json'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 502

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
