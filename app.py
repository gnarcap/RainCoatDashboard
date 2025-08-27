from flask import Flask, render_template_string
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import random

app = Flask(__name__)

# Metrics
raincoat_sales = Counter('raincoat_sales_total', 'Total raincoat sales')
raincoat_inventory = Gauge('raincoat_inventory_current', 'Current raincoat inventory')
raincoat_orders = Counter('raincoat_orders_total', 'Total raincoat orders')

@app.route('/')
def dashboard():
    if random.random() > 0.7:
        raincoat_sales.inc(random.randint(1, 3))
        raincoat_orders.inc(1)
    
    raincoat_inventory.set(random.randint(50, 200))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raincoat Dashboard - IIS</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial; margin: 20px; }
            .chart-container { width: 400px; height: 300px; display: inline-block; margin: 20px; }
        </style>
    </head>
    <body>
        <h1>Raincoat Business Dashboard</h1>
        <p><em>Running on IIS with Python FastCGI</em></p>
        
        <div class="chart-container">
            <canvas id="salesChart"></canvas>
        </div>
        <div class="chart-container">
            <canvas id="inventoryChart"></canvas>
        </div>
        
        <p><a href="/metrics">Prometheus Metrics</a></p>
        
        <script>
            const salesChart = new Chart(document.getElementById('salesChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Sales', 'Orders'],
                    datasets: [{
                        data: [{{ sales }}, {{ orders }}],
                        backgroundColor: ['#36A2EB', '#FF6384']
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: 'Sales & Orders' }}}
            });
            
            const inventoryChart = new Chart(document.getElementById('inventoryChart'), {
                type: 'bar',
                data: {
                    labels: ['Inventory'],
                    datasets: [{
                        label: 'Units',
                        data: [{{ inventory }}],
                        backgroundColor: '#4BC0C0'
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: 'Current Stock' }}}
            });
            
            setTimeout(() => location.reload(), 10000);
        </script>
    </body>
    </html>
    ''', 
    sales=int(raincoat_sales._value._value), 
    inventory=int(raincoat_inventory._value), 
    orders=int(raincoat_orders._value._value))

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# IIS FastCGI entry point
def application(environ, start_response):
    return app(environ, start_response)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

