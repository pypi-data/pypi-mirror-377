#!/bin/bash
# MultiBrain Deployment Script
# This script sets up MultiBrain on a production server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/multibrain"
SERVICE_USER="multibrain"
PYTHON_VERSION="3.11"

# Functions
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

print_status "Starting MultiBrain deployment..."

# Update system
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
print_status "Installing system dependencies..."
apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev \
    nginx \
    nodejs \
    npm \
    git \
    curl \
    build-essential

# Create service user
if ! id "$SERVICE_USER" &>/dev/null; then
    print_status "Creating service user..."
    useradd -r -s /bin/bash -m -d /home/$SERVICE_USER $SERVICE_USER
fi

# Create installation directory
print_status "Creating installation directory..."
mkdir -p $INSTALL_DIR
chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR

# Clone or update repository
print_status "Setting up MultiBrain code..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd $INSTALL_DIR
    sudo -u $SERVICE_USER git pull
else
    cd /opt
    sudo -u $SERVICE_USER git clone https://spacecruft.org/deepcrayon/multibrain $INSTALL_DIR
    cd $INSTALL_DIR
fi

# Setup Python virtual environment
print_status "Setting up Python virtual environment..."
sudo -u $SERVICE_USER python${PYTHON_VERSION} -m venv venv
sudo -u $SERVICE_USER venv/bin/pip install --upgrade pip setuptools wheel

# Install Python dependencies
print_status "Installing Python dependencies..."
sudo -u $SERVICE_USER venv/bin/pip install -e .

# Build frontend
print_status "Building frontend..."
cd $INSTALL_DIR/frontend
sudo -u $SERVICE_USER npm install
sudo -u $SERVICE_USER npm run build

# Create logs directory
print_status "Creating logs directory..."
mkdir -p $INSTALL_DIR/logs
chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR/logs

# Setup systemd service
print_status "Setting up systemd service..."
cp $INSTALL_DIR/deploy/multibrain-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable multibrain-api

# Setup Nginx
print_status "Configuring Nginx..."
cp $INSTALL_DIR/deploy/nginx-multibrain.conf /etc/nginx/sites-available/multibrain

# Check if default site should be disabled
if [ -L /etc/nginx/sites-enabled/default ]; then
    print_warning "Disabling default Nginx site..."
    rm /etc/nginx/sites-enabled/default
fi

# Enable MultiBrain site
ln -sf /etc/nginx/sites-available/multibrain /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t

# Create environment file
print_status "Creating environment configuration..."
cat > $INSTALL_DIR/.env << EOF
# MultiBrain Production Configuration
MULTIBRAIN_ENV=production
MULTIBRAIN_LOG_LEVEL=info
MULTIBRAIN_CORS_ORIGINS=*
EOF

chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR/.env
chmod 600 $INSTALL_DIR/.env

# Start services
print_status "Starting services..."
systemctl start multibrain-api
systemctl reload nginx

# Check service status
sleep 3
if systemctl is-active --quiet multibrain-api; then
    print_status "MultiBrain API is running!"
else
    print_error "MultiBrain API failed to start. Check logs with: journalctl -u multibrain-api"
    exit 1
fi

# Print success message
print_status "Deployment complete!"
echo ""
echo "MultiBrain is now running at:"
echo "  http://$(hostname -I | awk '{print $1}'):80"
echo ""
echo "To check service status:"
echo "  systemctl status multibrain-api"
echo ""
echo "To view logs:"
echo "  journalctl -u multibrain-api -f"
echo ""
echo "To configure SSL/TLS:"
echo "  certbot --nginx -d yourdomain.com"