// Chart initialization
let chart;

function initChart(sales, orders, inventory) {
    const ctx = document.getElementById('chart');
    if (ctx) {
        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Sales', 'Orders', 'Inventory'],
                datasets: [{
                    data: [sales, orders, inventory],
                    backgroundColor: ['#36A2EB', '#FF6384', '#4BC0C0']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Form handling
document.addEventListener('DOMContentLoaded', function() {
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.onsubmit = function(e) {
            e.preventDefault();
            
            const formData = {
                customer: document.getElementById('customer').value,
                quantity: parseInt(document.getElementById('quantity').value),
                price: parseFloat(document.getElementById('price').value)
            };
            
            fetch('/order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to add order');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error adding order');
            });
        };
    }
});

// SFTP transfer function
function transferData() {
    fetch('/transfer')
        .then(response => response.json())
        .then(data => {
            alert(data.success ? 'Transfer successful' : 'Transfer failed');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Transfer error');
        });
}
