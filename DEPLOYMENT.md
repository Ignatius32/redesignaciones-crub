# Deployment Guide for CRUB Course Team Management System

## Overview

This FastAPI application needs to be deployed using a reverse proxy approach since FastAPI is an ASGI application, not WSGI. The recommended approach is to run the application with uvicorn and proxy requests through Apache.

## Quick Deployment Steps

### 1. Upload Files to Server

Upload all the project files to your server (you can use scp, rsync, or git clone):

```bash
# If using git:
cd /var/www
sudo git clone https://github.com/your-repo/redesignaciones-crub.git
cd redesignaciones-crub

# Or if uploading files manually, ensure they're in:
# /var/www/redesignaciones-crub/
```

### 2. Run the Deployment Script

```bash
cd /var/www/redesignaciones-crub
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

### 3. Configure API Credentials

Edit the environment file with your actual credentials:

```bash
sudo nano /var/www/redesignaciones-crub/.env
```

Add your Google Sheets and Huayca API credentials.

### 4. Update Apache Configuration

Add this configuration to your Apache virtual host file (`/etc/apache2/sites-available/000-default-le-ssl.conf`):

```apache
# === REDESIGNACIONES CRUB APPLICATION ===
<Location /redesignaciones-crub>
    ProxyPreserveHost On
    ProxyPass http://127.0.0.1:8001/
    ProxyPassReverse http://127.0.0.1:8001/
    
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-For %{REMOTE_ADDR}s
</Location>
```

### 5. Reload Apache

```bash
sudo systemctl reload apache2
```

### 6. Test the Application

Your application should now be available at:
- https://huayca.crub.uncoma.edu.ar/redesignaciones-crub/
- https://huayca.crub.uncoma.edu.ar/redesignaciones-crub/docs (API documentation)

## Manual Deployment (Alternative)

If you prefer to deploy manually:

### 1. Create Directory and Copy Files

```bash
sudo mkdir -p /var/www/redesignaciones-crub
sudo chown www-data:www-data /var/www/redesignaciones-crub
# Copy your files to this directory
```

### 2. Set Up Virtual Environment

```bash
cd /var/www/redesignaciones-crub
sudo -u www-data python3 -m venv venv
sudo -u www-data venv/bin/pip install -r requirements.txt
sudo -u www-data venv/bin/pip install gunicorn uvicorn[standard]
```

### 3. Create Environment File

```bash
sudo -u www-data cp .env.example .env  # or create from scratch
sudo nano .env  # Add your credentials
```

### 4. Install and Start Service

```bash
sudo cp redesignaciones-crub.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable redesignaciones-crub
sudo systemctl start redesignaciones-crub
```

### 5. Enable Apache Modules and Add Configuration

```bash
sudo a2enmod proxy proxy_http headers
# Add the Location block to your Apache virtual host
sudo systemctl reload apache2
```

## Service Management

```bash
# Check status
sudo systemctl status redesignaciones-crub

# View logs
sudo journalctl -u redesignaciones-crub -f

# Restart service
sudo systemctl restart redesignaciones-crub

# Stop service
sudo systemctl stop redesignaciones-crub
```

## Troubleshooting

### Check if the service is running:
```bash
sudo systemctl status redesignaciones-crub
curl http://127.0.0.1:8001/health
```

### Check logs:
```bash
sudo journalctl -u redesignaciones-crub -n 50
```

### Test Apache proxy:
```bash
curl -H "Host: huayca.crub.uncoma.edu.ar" https://localhost/redesignaciones-crub/health
```

## Application URLs

Once deployed, your application will be available at:

- **Main page**: https://huayca.crub.uncoma.edu.ar/redesignaciones-crub/
- **API Documentation**: https://huayca.crub.uncoma.edu.ar/redesignaciones-crub/docs
- **Alternative docs**: https://huayca.crub.uncoma.edu.ar/redesignaciones-crub/redoc
- **Health check**: https://huayca.crub.uncoma.edu.ar/redesignaciones-crub/health
- **All designaciones**: https://huayca.crub.uncoma.edu.ar/redesignaciones-crub/designaciones
- **By department**: https://huayca.crub.uncoma.edu.ar/redesignaciones-crub/departamentos

## Security Notes

1. Make sure to change the default admin password in the `.env` file
2. Keep your API credentials secure
3. The service runs as `www-data` user for security
4. Sensitive directories are protected in the systemd service configuration

## Performance Notes

- The service is configured with a single worker by default
- You can increase workers in the `production_server.py` file if needed
- Monitor performance and adjust as necessary
