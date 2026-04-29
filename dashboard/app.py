from flask import Flask, jsonify, render_template_string
import json

app = Flask(__name__)

# Данные стратегии
STRATEGY_DATA = {
    "name": "Structure H1 — Si Futures",
    "params": {
        "timeframe": "60 мин",
        "swing_left": 3,
        "swing_right": 5,
        "atr_period": 14,
        "atr_mult": 1.0,
        "tp_ratio": 1.5
    },
    "results": {
        "trades": 29,
        "pnl_points": 5014.8,
        "winrate": 69.0,
        "max_dd": 765.6,
        "sharpe": 2.83,
        "avg_trade": 172.9
    },
    "profitability": {
        "capital": 100000,
        "gross_profit": 50148,
        "commission": 290,
        "slippage": 1160,
        "tax": 6331,
        "net_profit": 42367,
        "roi_percent": 42.4,
        "monthly_roi": 14.1,
        "max_dd_rub": 7656,
        "max_dd_percent": 7.7
    }
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 {
            font-size: 2rem;
            color: #00e676;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .card {
            background: #141414;
            border: 1px solid #222;
            border-radius: 12px;
            padding: 20px;
            transition: border-color 0.3s;
        }
        .card:hover { border-color: #333; }
        .card h3 {
            font-size: 0.85rem;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }
        .card .value {
            font-size: 1.8rem;
            font-weight: 700;
        }
        .positive { color: #00e676; }
        .negative { color: #ff3b3b; }
        .neutral { color: #ffd700; }
        .section {
            background: #141414;
            border: 1px solid #222;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .section h2 {
            color: #00e676;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #222;
        }
        th { color: #666; font-weight: 500; }
        .footer {
            text-align: center;
            color: #444;
            margin-top: 40px;
            font-size: 0.85rem;
        }
        .highlight {
            background: linear-gradient(90deg, #00e67622, transparent);
            border-left: 3px solid #00e676;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        .api-section {
            background: #0f0f0f;
            border: 1px solid #1a1a1a;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }
        code {
            background: #1a1a1a;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #ffd700;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Стратегия Structure H1</h1>
        <p class="subtitle">Фьючерс Si (USD/RUB) | Таймфрейм 60 мин</p>

        <div class="grid">
            <div class="card">
                <h3>Чистая прибыль</h3>
                <div class="value positive">+{{ data.profitability.net_profit|int:, }} ₽</div>
            </div>
            <div class="card">
                <h3>Доходность (3 мес)</h3>
                <div class="value positive">+{{ data.profitability.roi_percent }}%</div>
            </div>
            <div class="card">
                <h3>Sharpe Ratio</h3>
                <div class="value positive">{{ data.results.sharpe }}</div>
            </div>
            <div class="card">
                <h3>Winrate</h3>
                <div class="value neutral">{{ data.results.winrate }}%</div>
            </div>
            <div class="card">
                <h3>Сделок</h3>
                <div class="value">{{ data.results.trades }}</div>
            </div>
            <div class="card">
                <h3>Max просадка</h3>
                <div class="value negative">{{ data.profitability.max_dd_percent }}%</div>
            </div>
        </div>

        <div class="highlight">
            <strong>💡 Параметры стратегии:</strong> left={{ data.params.swing_left }}, right={{ data.params.swing_right }}, 
            ATR×{{ data.params.atr_mult }}, TP={{ data.params.tp_ratio }}×
        </div>

        <div class="section">
            <h2>📈 Детальная статистика</h2>
            <table>
                <tr><th>Показатель</th><th>Значение</th></tr>
                <tr><td>PnL (пункты)</td><td class="positive">+{{ data.results.pnl_points }}</td></tr>
                <tr><td>Средняя сделка</td><td>{{ data.results.avg_trade }} п</td></tr>
                <tr><td>Max просадка (пункты)</td><td>{{ data.results.max_dd }}</td></tr>
                <tr><td>Комиссия</td><td>{{ data.profitability.commission }} ₽</td></tr>
                <tr><td>Проскальзывание</td><td>{{ data.profitability.slippage }} ₽</td></tr>
                <tr><td>Налог (13%)</td><td>{{ data.profitability.tax }} ₽</td></tr>
                <tr><td>Капитал</td><td>{{ data.profitability.capital|int:, }} ₽</td></tr>
                <tr><td>Доходность в месяц</td><td class="positive">+{{ data.profitability.monthly_roi }}%</td></tr>
            </table>
        </div>

        <div class="section">
            <h2>🔌 API (есть бэкенд!)</h2>
            <p>Эта страница работает на Flask. Данные можно получить через API:</p>
            <div class="api-section">
                <code>GET /api/strategy</code> — JSON со всей статистикой<br>
                <code>GET /api/health</code> — проверка работоспособности
            </div>
        </div>

        <div class="footer">
            Сгенерировано Ильей | Стратегия: Structure H1 | Si Futures
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, data=STRATEGY_DATA)

@app.route('/api/strategy')
def api_strategy():
    return jsonify(STRATEGY_DATA)

@app.route('/api/health')
def api_health():
    return jsonify({"status": "ok", "service": "strategy-dashboard"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
