# Raincoat Dashboard - Python Web App for IIS

A Flask-based business dashboard application designed to run on Windows IIS with FastCGI.

## Directory Structure

```
RainCoatDashboard/
├── app.py                 # Main Flask application
├── web.config            # IIS FastCGI configuration
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheet
│   ├── js/
│   │   └── app.js        # JavaScript functionality
│   └── images/           # (empty, for future images)
├── templates/
│   ├── base.html         # Base HTML template
│   └── index.html        # Dashboard template
└── logs/                 # (empty, for application logs)
```

## Features

- **Complete Flask app** with SQLite database
- **SFTP transfer functionality** for database backups
- **Prometheus metrics** endpoint at `/metrics`
- **Responsive design** with CSS styling
- **Pre-populated database** with 20 sample raincoat orders
- **Revenue tracking** with price calculations
- **Real-time charts** using Chart.js

## Local Development Testing

### Prerequisites
- Python 3.9+ installed
- pip package manager

### Quick Start
```bash
# Navigate to project directory
cd /Users/gccapos/Documents/auto/RainCoatDashboard

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### Test in Browser
1. Open browser to `http://127.0.0.1:5000`
2. You should see the Raincoat Business Dashboard
3. Test functionality:
   - View pre-populated orders and revenue
   - Add new orders using the form
   - Check metrics at `http://127.0.0.1:5000/metrics`
   - Test SFTP transfer (will fail without SFTP server)

## IIS Deployment

### Prerequisites
- Windows Server with IIS installed
- Python 3.9+ installed on server
- IIS FastCGI module enabled

### Deployment Steps

1. **Copy files to IIS directory:**
   ```cmd
   xcopy /E /I RainCoatDashboard C:\inetpub\wwwroot\raincoat-demo
   ```

2. **Install Python dependencies:**
   ```cmd
   cd C:\inetpub\wwwroot\raincoat-demo
   C:\Python39\python.exe -m pip install -r requirements.txt
   ```

3. **Enable FastCGI in IIS:**
   ```cmd
   C:\Python39\Scripts\wfastcgi-enable.exe
   ```

4. **Create IIS site:**
   ```powershell
   Import-Module WebAdministration
   New-IISSite -Name 'RaincoatDemo' -PhysicalPath 'C:\inetpub\wwwroot\raincoat-demo' -Port 80
   ```

5. **Set permissions:**
   ```cmd
   icacls C:\inetpub\wwwroot\raincoat-demo /grant IIS_IUSRS:F
   ```

### Test IIS Deployment
1. Open browser to `http://your-server-ip`
2. Verify dashboard loads with sample data
3. Test adding new orders
4. Check that database file is created: `C:\inetpub\wwwroot\raincoat-demo\raincoat.db`

## Configuration

### SFTP Settings
Update `app.py` line 42 to configure SFTP server:
```python
ssh.connect('YOUR_SFTP_SERVER_IP', username='sftpuser', password='YOUR_PASSWORD')
```

### Database Location
- **Development:** `raincoat.db` in project root
- **IIS Production:** `C:\inetpub\wwwroot\raincoat-demo\raincoat.db`

## Troubleshooting

### Common Issues
- **500 Error:** Check IIS logs in `C:\inetpub\logs\LogFiles\W3SVC1\`
- **Python not found:** Verify Python path in `web.config`
- **Database permissions:** Ensure IIS_IUSRS has write access to app directory
- **FastCGI errors:** Run `wfastcgi-enable` and restart IIS

### Logs
- **IIS logs:** `C:\inetpub\logs\LogFiles\W3SVC1\`
- **Application logs:** `logs/` directory (if configured)
- **Windows Event Viewer:** Application logs

## API Endpoints

- `GET /` - Main dashboard
- `POST /order` - Add new order (JSON)
- `GET /transfer` - Transfer database to SFTP
- `GET /metrics` - Prometheus metrics

## Development Notes

- Uses SQLite for simplicity (consider PostgreSQL/SQL Server for production)
- SFTP transfer requires paramiko library
- Metrics compatible with Prometheus monitoring
- Templates use Jinja2 inheritance
- Static files served by IIS in production
