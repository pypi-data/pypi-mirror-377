# MultiBrain Deployment Files

This directory contains all the necessary files for deploying MultiBrain to a production server.

## Files

- **multibrain-api.service** - Systemd service file for running the API server
- **nginx-multibrain.conf** - Nginx configuration for reverse proxy and static file serving
- **production.env** - Production environment variables template
- **deploy.sh** - Automated deployment script for Ubuntu/Debian servers

## Quick Deployment

1. **Run the deployment script** (as root):
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Configure your domain** (optional):
   - Edit `/etc/nginx/sites-available/multibrain`
   - Replace `server_name _;` with `server_name yourdomain.com;`
   - Run `sudo nginx -t && sudo systemctl reload nginx`

3. **Setup SSL/TLS** (recommended):
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

## Manual Deployment

If you prefer manual deployment or need to customize the setup:

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv nginx nodejs npm
```

### 2. Create Service User

```bash
sudo useradd -r -s /bin/bash -m -d /home/multibrain multibrain
```

### 3. Setup Application

```bash
# Clone repository
cd /opt
sudo -u multibrain git clone https://spacecruft.org/deepcrayon/multibrain
cd multibrain

# Setup Python environment
sudo -u multibrain python3.11 -m venv venv
sudo -u multibrain venv/bin/pip install -e .

# Build frontend
cd frontend
sudo -u multibrain npm install
sudo -u multibrain npm run build
```

### 4. Configure Services

```bash
# Copy systemd service
sudo cp deploy/multibrain-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable multibrain-api

# Configure Nginx
sudo cp deploy/nginx-multibrain.conf /etc/nginx/sites-available/multibrain
sudo ln -s /etc/nginx/sites-available/multibrain /etc/nginx/sites-enabled/
sudo nginx -t
```

### 5. Start Services

```bash
sudo systemctl start multibrain-api
sudo systemctl reload nginx
```

## Environment Variables

Copy `production.env` to `/opt/multibrain/.env` and customize as needed:

- `MULTIBRAIN_CORS_ORIGINS` - Set to your domain(s)
- `MULTIBRAIN_LOG_LEVEL` - Set to `info` for production
- `MULTIBRAIN_SERVE_STATIC` - Set to `true` if not using Nginx

## Monitoring

Check service status:
```bash
sudo systemctl status multibrain-api
```

View logs:
```bash
sudo journalctl -u multibrain-api -f
```

Check API health:
```bash
curl http://localhost:8000/health
```

## Updating

To update to the latest version:

```bash
cd /opt/multibrain
sudo -u multibrain git pull
sudo -u multibrain venv/bin/pip install -U .
cd frontend
sudo -u multibrain npm install
sudo -u multibrain npm run build
sudo systemctl restart multibrain-api
```

## Troubleshooting

1. **502 Bad Gateway**: Check if the API service is running
2. **CORS errors**: Verify MULTIBRAIN_CORS_ORIGINS in .env
3. **Static files not loading**: Check Nginx configuration and file permissions
4. **SSE not working**: Ensure Nginx SSE configuration is correct

For more details, see the main [Deployment Guide](../docs/DEPLOYMENT.md).