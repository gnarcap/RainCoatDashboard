from flask import Flask, render_template_string, request, jsonify
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import sqlite3
import paramiko
import random
import datetime

app = Flask(__name__)
raincoat_sales = Counter('raincoat_sales_total', 'Total raincoat sales')
raincoat_inventory = Gauge('raincoat_inventory_current', 'Current raincoat inventory')
raincoat_orders = Counter('raincoat_orders_total', 'Total raincoat orders')

def init_db():
    conn = sqlite3.connect('raincoat.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer TEXT, quantity INTEGER, price REAL, timestamp TEXT)''')
    
    # Check if database is empty and prepopulate
    count = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    if count == 0:
        customers = ['John Smith', 'Sarah Johnson', 'Mike Davis', 'Lisa Wilson', 'Tom Brown', 
                    'Emma Garcia', 'David Miller', 'Anna Taylor', 'Chris Anderson', 'Maria Rodriguez']
        
        for i in range(20):
            customer = random.choice(customers)
            quantity = random.randint(1, 5)
            price = round(random.uniform(25.99, 89.99), 2)
            days_ago = random.randint(0, 30)
            timestamp = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).isoformat()
            
            conn.execute('INSERT INTO orders (customer, quantity, price, timestamp) VALUES (?, ?, ?, ?)', 
                        (customer, quantity, price, timestamp))
    
    conn.commit()
    conn.close()

def transfer_to_sftp():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('SFTP_SERVER_IP', username='sftpuser', password='SftpPass123!')
        sftp = ssh.open_sftp()
        sftp.put('raincoat.db', '/sftp-data/raincoat.db')
        sftp.close()
        ssh.close()
        return True
    except:
        return False

@app.route('/')
def dashboard():
    conn = sqlite3.connect('raincoat.db')
    orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_revenue = conn.execute('SELECT SUM(quantity * price) FROM orders').fetchone()[0] or 0
    conn.close()
    
    if random.random() > 0.7:
        raincoat_sales.inc(random.randint(1, 3))
        raincoat_orders.inc(1)
    raincoat_inventory.set(random.randint(50, 200))
    
    return render_template_string('''<!DOCTYPE html>
<html>
<head>
    <title>Raincoat Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        form { margin: 20px 0; }
        input { margin: 5px; padding: 8px; }
        button { padding: 10px 15px; background: #007cba; color: white; border: none; cursor: pointer; }
        canvas { margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Raincoat Business Dashboard</h1>
    <form id="orderForm">
        <input type="text" id="customer" placeholder="Customer Name" required>
        <input type="number" id="quantity" placeholder="Quantity" required>
        <input type="number" id="price" placeholder="Price" step="0.01" required>
        <button type="submit">Add Order</button>
    </form>
    <div>
        <canvas id="chart" width="400" height="200"></canvas>
    </div>
    <p>Database Orders: {{ orders }}</p>
    <p>Total Revenue: ${{ "%.2f"|format(revenue) }}</p>
    <button onclick="transferData()">Transfer to SFTP</button>
    <p><a href="/metrics">Metrics</a></p>
    
    <script>
        const chart = new Chart(document.getElementById('chart'), {
            type: 'bar',
            data: {
                labels: ['Sales', 'Orders', 'Inventory'],
                datasets: [{
                    data: [{{ sales }}, {{ orders }}, {{ inventory }}],
                    backgroundColor: ['#36A2EB', '#FF6384', '#4BC0C0']
                }]
            }
        });
        
        document.getElementById('orderForm').onsubmit = function(e) {
            e.preventDefault();
            fetch('/order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    customer: document.getElementById('customer').value,
                    quantity: parseInt(document.getElementById('quantity').value),
                    price: parseFloat(document.getElementById('price').value)
                })
            }).then(() => location.reload());
        };
        
        function transferData() {
            fetch('/transfer').then(r => r.json()).then(d => 
                alert(d.success ? 'Transfer successful' : 'Transfer failed')
            );
        }
    </script>
</body>
</html>''', sales=int(raincoat_sales._value._value), inventory=int(raincoat_inventory._value), orders=int(raincoat_orders._value._value), orders=orders, revenue=total_revenue)

@app.route('/order', methods=['POST'])
def add_order():
    data = request.get_json()
    conn = sqlite3.connect('raincoat.db')
    conn.execute('INSERT INTO orders (customer, quantity, price, timestamp) VALUES (?, ?, ?, ?)', 
                (data['customer'], data['quantity'], data['price'], datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/transfer')
def transfer():
    success = transfer_to_sftp()
    return jsonify({'success': success})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# WSGI callable for IIS
def application(environ, start_response):
    init_db()
    return app(environ, start_response)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
