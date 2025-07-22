#!/bin/bash
# Deployment script for CRUB Course Team Management System (redesignaciones)

set -e

echo "=== CRUB Course Team Management System Deployment ==="
echo "This script will deploy the redesignaciones application to Apache"
echo ""

# Configuration
APP_NAME="redesignaciones-crub"
APP_DIR="/var/www/$APP_NAME"
SERVICE_NAME="$APP_NAME.service"
VENV_DIR="$APP_DIR/venv"
APACHE_CONF="/etc/apache2/sites-available/000-default-le-ssl.conf"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

echo "1. Creating application directory..."
mkdir -p $APP_DIR
chown www-data:www-data $APP_DIR

echo "2. Copying application files..."
# Copy all files except local development files
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='.env' --exclude='venv' ./ $APP_DIR/
chown -R www-data:www-data $APP_DIR

echo "3. Setting up Python virtual environment..."
sudo -u www-data python3 -m venv $VENV_DIR
sudo -u www-data $VENV_DIR/bin/pip install --upgrade pip
sudo -u www-data $VENV_DIR/bin/pip install -r $APP_DIR/requirements.txt

echo "4. Installing additional dependencies for ASGI..."
sudo -u www-data $VENV_DIR/bin/pip install gunicorn uvicorn[standard]

echo "5. Creating environment file..."
if [ ! -f "$APP_DIR/.env" ]; then
    cat > $APP_DIR/.env << EOF
# Production configuration
DEBUG=false
HOST=127.0.0.1
PORT=8001

# Admin credentials (change these!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here

# Add your Google Sheets and Huayca API credentials here
# GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/credentials.json
# HUAYCA_API_KEY=your_api_key_here
EOF
    chown www-data:www-data $APP_DIR/.env
    chmod 600 $APP_DIR/.env
    echo "Created .env file - PLEASE EDIT IT WITH YOUR CREDENTIALS!"
fi

echo "6. Installing systemd service..."
cp $APP_DIR/$SERVICE_NAME /etc/systemd/system/
systemctl daemon-reload
systemctl enable $SERVICE_NAME

echo "7. Testing the application..."
echo "Starting service temporarily to test..."
sudo -u www-data $VENV_DIR/bin/python $APP_DIR/production_server.py &
APP_PID=$!
sleep 5

# Test if the application is responding
if curl -f http://127.0.0.1:8001/health > /dev/null 2>&1; then
    echo "✓ Application is responding correctly"
    kill $APP_PID
else
    echo "✗ Application test failed"
    kill $APP_PID 2>/dev/null || true
    echo "Check the logs and configuration"
    exit 1
fi

echo "8. Updating Apache configuration..."
echo ""
echo "Please add the following configuration to your Apache virtual host:"
echo "File: $APACHE_CONF"
echo ""
cat $APP_DIR/apache_config_snippet.conf
echo ""

echo "9. Enabling required Apache modules..."
a2enmod proxy
a2enmod proxy_http
a2enmod headers
systemctl reload apache2

echo "10. Starting the service..."
systemctl start $SERVICE_NAME
systemctl status $SERVICE_NAME

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit $APP_DIR/.env with your API credentials"
echo "2. Add the Apache configuration snippet to your virtual host"
echo "3. Reload Apache: systemctl reload apache2"
echo "4. Test the application at: https://huayca.crub.uncoma.edu.ar/redesignaciones-crub"
echo ""
echo "Service management:"
echo "  Start:   systemctl start $SERVICE_NAME"
echo "  Stop:    systemctl stop $SERVICE_NAME"
echo "  Restart: systemctl restart $SERVICE_NAME"
echo "  Status:  systemctl status $SERVICE_NAME"
echo "  Logs:    journalctl -u $SERVICE_NAME -f"
echo ""
echo "Application logs: journalctl -u $SERVICE_NAME"
