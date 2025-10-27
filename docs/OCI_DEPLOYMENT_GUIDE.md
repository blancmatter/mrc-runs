# OCI Deployment Guide: Complete Setup Instructions

This guide provides step-by-step instructions for deploying the MRC Runs Django application to Oracle Cloud Infrastructure (OCI) Always Free tier.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [OCI Account Setup](#oci-account-setup)
3. [Infrastructure Provisioning](#infrastructure-provisioning)
4. [Server Configuration](#server-configuration)
5. [Database Setup](#database-setup)
6. [Application Deployment](#application-deployment)
7. [Web Server Configuration](#web-server-configuration)
8. [SSL Certificate Setup](#ssl-certificate-setup)
9. [OCI CLI Setup](#oci-cli-setup)
10. [GitHub Actions CI/CD](#github-actions-cicd)
11. [Monitoring & Maintenance](#monitoring--maintenance)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- GitHub account with repository access
- Email address for OCI account
- Credit card for OCI verification (not charged on free tier)
- SSH client installed on your computer
- Basic command-line knowledge

### Optional
- Domain name ($10-15/year)
- Terminal multiplexer (tmux/screen) for long-running tasks

---

## OCI Account Setup

### Step 1: Create OCI Account

1. Visit https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Fill in registration details:
   - Country/Territory
   - Account Name (choose carefully, cannot change later)
   - Email address
   - Password
4. Verify email address
5. Enter payment information:
   - Used only for verification
   - Free tier resources are never charged
   - Optional: Set up billing alerts for paid resources
6. **Select Home Region** (IMPORTANT):
   - This choice is permanent
   - Choose closest to your users for best performance
   - Recommended: US East (Ashburn) or UK South (London)
7. Wait for account provisioning (5-10 minutes)
8. Log in to https://cloud.oracle.com

### Step 2: Navigate OCI Console

Familiarize yourself with the console:
- **Navigation Menu** (hamburger icon top-left)
- **Compartments**: Logical containers for resources
- **Tenancy**: Your OCI account
- **Home Region**: Where your Always Free resources live

Note your **Tenancy OCID** (needed later):
- Profile menu → Tenancy → Copy OCID

---

## Infrastructure Provisioning

### Step 1: Create Compartment

Compartments organize your resources:

1. Navigation Menu → Identity & Security → Compartments
2. Click "Create Compartment"
3. Configure:
   - **Name**: `mrc-runs-prod`
   - **Description**: Production environment for MRC Runs application
   - **Parent Compartment**: (root)
4. Click "Create Compartment"
5. Note the **Compartment OCID** (needed later)

### Step 2: Create Virtual Cloud Network (VCN)

1. Navigation Menu → Networking → Virtual Cloud Networks
2. Click "Start VCN Wizard"
3. Select "Create VCN with Internet Connectivity"
4. Click "Start VCN Wizard"
5. Configure:
   - **VCN Name**: `mrc-runs-vcn`
   - **Compartment**: `mrc-runs-prod`
   - **VCN CIDR Block**: `10.0.0.0/16`
   - **Public Subnet CIDR Block**: `10.0.1.0/24`
   - **Private Subnet CIDR Block**: `10.0.2.0/24` (optional)
6. Click "Next" → "Create"
7. Wait for resources to be created

### Step 3: Configure Security List

Allow HTTP, HTTPS, and SSH traffic:

1. Navigate to your VCN: Networking → Virtual Cloud Networks → `mrc-runs-vcn`
2. Click "Security Lists" → "Default Security List for mrc-runs-vcn"
3. Click "Add Ingress Rules"

**Add these rules:**

**Rule 1: HTTP**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: TCP
- Destination Port Range: `80`
- Description: `HTTP traffic`

**Rule 2: HTTPS**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: TCP
- Destination Port Range: `443`
- Description: `HTTPS traffic`

**Rule 3: SSH (Restrict to your IP!)**
- Source CIDR: `YOUR.PUBLIC.IP.ADDRESS/32` (find at https://whatismyipaddress.com)
- IP Protocol: TCP
- Destination Port Range: `22`
- Description: `SSH from my IP`

### Step 4: Create SSH Key Pair

On your local machine:

```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh

# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oci_mrc_runs -C "mrc-runs-deployment"

# Press Enter for no passphrase (or set one if you prefer)

# View public key (you'll upload this to OCI)
cat ~/.ssh/oci_mrc_runs.pub
```

### Step 5: Launch Compute Instance

1. Navigation Menu → Compute → Instances
2. Click "Create Instance"
3. Configure:

**Name and Placement**
- **Name**: `mrc-runs-app-server`
- **Create in compartment**: `mrc-runs-prod`
- **Availability Domain**: AD-1 (or any available)
- **Fault Domain**: Leave default

**Image and Shape**
- Click "Change Image"
  - **Image**: Canonical Ubuntu 22.04
  - Click "Select Image"
- Click "Change Shape"
  - **Shape series**: Ampere
  - **Shape**: VM.Standard.A1.Flex
  - **Number of OCPUs**: 2 (start with 2, can use up to 4 total)
  - **Amount of memory (GB)**: 12
  - Click "Select Shape"

**Networking**
- **Virtual cloud network**: `mrc-runs-vcn`
- **Subnet**: Public Subnet (10.0.1.0/24)
- **Public IP address**: Assign a public IPv4 address

**Add SSH Keys**
- Paste your public key content from `~/.ssh/oci_mrc_runs.pub`
- Or upload the `.pub` file

**Boot Volume**
- **Boot volume size (GB)**: 50
- Leave encryption options as default

4. Click "Create"
5. Wait for instance to reach "Running" state (2-3 minutes)
6. **Note the Public IP address** (you'll need this constantly)

---

## Server Configuration

### Step 1: Connect to Instance

```bash
# SSH into your instance
ssh -i ~/.ssh/oci_mrc_runs ubuntu@YOUR.INSTANCE.PUBLIC.IP

# If connection refused, check:
# 1. Security List allows your IP on port 22
# 2. Instance is in "Running" state
# 3. Using correct username (ubuntu for Ubuntu, opc for Oracle Linux)
```

### Step 2: Initial Server Setup

Run these commands on the OCI instance:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3-pip \
    python3-venv \
    nginx \
    postgresql \
    postgresql-contrib \
    git \
    ufw \
    supervisor \
    certbot \
    python3-certbot-nginx \
    build-essential \
    libpq-dev

# Configure firewall (UFW)
sudo ufw allow 22/tcp  comment 'SSH'
sudo ufw allow 80/tcp  comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw enable
# Type 'y' to confirm

# Set hostname
sudo hostnamectl set-hostname mrc-runs-prod

# Set timezone to UTC
sudo timedatectl set-timezone UTC

# Verify settings
hostnamectl
timedatectl
```

### Step 3: Create Application User

```bash
# Create user for running the application
sudo useradd -m -s /bin/bash mrcuser
sudo usermod -aG www-data mrcuser

# Create application directories
sudo mkdir -p /opt/mrc-runs/{app,venv,logs,backups}
sudo chown -R mrcuser:www-data /opt/mrc-runs
sudo chmod -R 755 /opt/mrc-runs
```

### Step 4: Configure Swap Space

```bash
# Create 2GB swap file (helps with stability)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify swap is active
free -h
```

### Step 5: Enable Automatic Security Updates

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
# Select "Yes" when prompted
```

---

## Database Setup

### Step 1: Configure PostgreSQL

```bash
# Switch to postgres user
sudo -i -u postgres

# Create database and user
psql << EOF
CREATE DATABASE mrc_runs;
CREATE USER mrcadmin WITH PASSWORD 'CHANGE_THIS_TO_SECURE_PASSWORD';
ALTER ROLE mrcadmin SET client_encoding TO 'utf8';
ALTER ROLE mrcadmin SET default_transaction_isolation TO 'read committed';
ALTER ROLE mrcadmin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE mrc_runs TO mrcadmin;
\\q
EOF

# Exit postgres user
exit
```

### Step 2: Secure PostgreSQL

```bash
# Edit PostgreSQL config to listen only on localhost
sudo nano /etc/postgresql/14/main/postgresql.conf

# Find and set:
# listen_addresses = 'localhost'

# Save and exit (Ctrl+X, Y, Enter)

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify PostgreSQL is running
sudo systemctl status postgresql
```

### Step 3: Test Database Connection

```bash
# Test connection (you'll be prompted for password)
psql -U mrcadmin -d mrc_runs -h localhost

# If successful, you'll see:
# mrc_runs=>

# Type \q to exit
\q
```

---

## Application Deployment

### Step 1: Clone Repository

```bash
# Switch to application user
sudo su - mrcuser

# Navigate to app directory
cd /opt/mrc-runs

# Clone repository (replace with your repo URL)
git clone https://github.com/blancmatter/mrc-runs.git app

# Verify files
ls -la app/
```

### Step 2: Set Up Python Environment

```bash
# Still as mrcuser
cd /opt/mrc-runs

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install application dependencies
cd app
pip install -r requirements.txt

# Install production-specific packages
pip install gunicorn psycopg2-binary whitenoise python-decouple
```

### Step 3: Configure Environment Variables

```bash
# Create .env file
nano /opt/mrc-runs/.env
```

**Add this content (customize the values):**

```bash
# Django Settings
SECRET_KEY=GENERATE_A_VERY_LONG_RANDOM_STRING_HERE
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR.INSTANCE.IP

# Database
DATABASE_URL=postgresql://mrcadmin:YOUR_PASSWORD_HERE@localhost/mrc_runs

# Optional: Email settings (for future use)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
```

**Generate a secure SECRET_KEY:**
```python
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Save and exit (Ctrl+X, Y, Enter)

### Step 4: Update Django Settings for Production

```bash
# Edit settings.py
nano /opt/mrc-runs/app/mrc_runs/settings.py
```

**Make these changes:**

```python
# At the top, add:
from decouple import config
from dj_database_url import parse as db_url

# Replace SECRET_KEY line with:
SECRET_KEY = config('SECRET_KEY')

# Replace DEBUG line with:
DEBUG = config('DEBUG', default=False, cast=bool)

# Replace ALLOWED_HOSTS with:
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Replace DATABASES with:
DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///db.sqlite3',
        cast=db_url
    )
}

# Add at the end:
# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add WhiteNoise to MIDDLEWARE (after SecurityMiddleware):
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    # ... rest of middleware
]
```

### Step 5: Run Migrations and Collect Static Files

```bash
# Make sure venv is activated
source /opt/mrc-runs/venv/bin/activate
cd /opt/mrc-runs/app

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
# Follow prompts to create admin account
```

### Step 6: Test Application with Gunicorn

```bash
# Test Gunicorn
cd /opt/mrc-runs/app
gunicorn --bind 0.0.0.0:8000 mrc_runs.wsgi:application

# Visit http://YOUR.INSTANCE.IP:8000 in browser
# You should see your application!
# Press Ctrl+C to stop
```

**If it works, exit the mrcuser shell:**
```bash
exit  # Back to ubuntu user
```

---

## Web Server Configuration

### Step 1: Configure Gunicorn as a Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/gunicorn.service
```

**Add this content:**

```ini
[Unit]
Description=Gunicorn daemon for MRC Runs Django application
After=network.target

[Service]
User=mrcuser
Group=www-data
WorkingDirectory=/opt/mrc-runs/app
EnvironmentFile=/opt/mrc-runs/.env
ExecStart=/opt/mrc-runs/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/opt/mrc-runs/gunicorn.sock \
          --access-logfile /opt/mrc-runs/logs/gunicorn-access.log \
          --error-logfile /opt/mrc-runs/logs/gunicorn-error.log \
          mrc_runs.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Enable and start Gunicorn:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn

# Verify socket was created
ls -l /opt/mrc-runs/gunicorn.sock
# Should show: srwxrwxrwx ... mrcuser www-data ... gunicorn.sock
```

### Step 2: Configure Nginx

```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/mrc-runs
```

**Add this content (update YOUR_DOMAIN):**

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com YOUR.INSTANCE.IP;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client upload size limit
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /opt/mrc-runs/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/mrc-runs/app/media/;
        expires 7d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://unix:/opt/mrc-runs/gunicorn.sock;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

**Enable the site:**

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/mrc-runs /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# If test passes, restart Nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

**Test your application:**

Visit `http://YOUR.INSTANCE.IP` in your browser. You should see your Django application!

---

## SSL Certificate Setup

### Prerequisites
- Domain name pointing to your OCI instance IP
- Ports 80 and 443 open in OCI Security List
- Nginx running and accessible via HTTP

### Step 1: Configure DNS

Point your domain to the OCI instance:

**A Records** (at your domain registrar):
- `@` (root domain) → `YOUR.INSTANCE.IP`
- `www` → `YOUR.INSTANCE.IP`

Wait 5-10 minutes for DNS propagation, then verify:

```bash
# Check DNS resolution
nslookup your-domain.com
# Should return YOUR.INSTANCE.IP
```

### Step 2: Obtain SSL Certificate

```bash
# Install Certbot (if not already installed)
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts:
# 1. Enter email address
# 2. Agree to Terms of Service (A)
# 3. Share email with EFF (Y/N - your choice)
# 4. Redirect HTTP to HTTPS? Choose option 2 (Redirect)

# Certbot will automatically configure Nginx for HTTPS!
```

### Step 3: Verify SSL

Visit `https://your-domain.com` - you should see:
- 🔒 Secure connection
- Your Django application
- Automatic redirect from HTTP to HTTPS

**Test SSL configuration:**
- Visit https://www.ssllabs.com/ssltest/
- Enter your domain
- Should get A or A+ rating

### Step 4: Configure Auto-Renewal

```bash
# Test renewal process
sudo certbot renew --dry-run

# If successful, renewal is already configured automatically!
# Certificates will auto-renew 30 days before expiration
```

---

## OCI CLI Setup

The OCI CLI allows you to manage OCI resources from your local machine and is essential for GitHub Actions deployment.

### Installation

**Mac/Linux:**
```bash
# Install via script
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Or via Homebrew (Mac)
brew install oci-cli

# Verify installation
oci --version
```

**Windows:**
1. Download MSI from: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/climanualinst.htm
2. Run installer
3. Verify in PowerShell: `oci --version`

### Configuration

```bash
# Start configuration wizard
oci setup config

# You'll be prompted for:
# 1. Location for config [~/.oci/config]: Press Enter
# 2. User OCID: Get from OCI Console → Profile → User Settings → Copy OCID
# 3. Tenancy OCID: Get from OCI Console → Profile → Tenancy → Copy OCID
# 4. Region: Your home region (e.g., us-ashburn-1)
# 5. Generate new API key? Y
# 6. Key location [~/.oci/oci_api_key.pem]: Press Enter
# 7. Passphrase (optional): Press Enter to skip

# The CLI will generate a public/private key pair
```

### Upload Public Key to OCI

```bash
# View public key
cat ~/.oci/oci_api_key_public.pem

# Copy the entire content (including BEGIN/END lines)

# Upload to OCI:
# 1. OCI Console → Profile → User Settings
# 2. Resources → API Keys
# 3. Add API Key
# 4. Paste Public Key
# 5. Add
```

### Test Configuration

```bash
# List regions
oci iam region list

# List your compute instances
oci compute instance list --compartment-id YOUR_COMPARTMENT_OCID

# If these work, you're good to go!
```

---

## GitHub Actions CI/CD

### Step 1: Prepare Deployment Script on Server

```bash
# SSH to OCI instance
ssh -i ~/.ssh/oci_mrc_runs ubuntu@YOUR.INSTANCE.IP

# Create deployment script
sudo nano /opt/mrc-runs/deploy.sh
```

**Add this content:**

```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Navigate to app directory
cd /opt/mrc-runs/app

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Activate virtual environment
source /opt/mrc-runs/venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Restart Gunicorn
echo "♻️ Restarting application..."
sudo systemctl restart gunicorn

# Reload Nginx
sudo systemctl reload nginx

# Check services
echo "✅ Checking service status..."
sudo systemctl is-active gunicorn
sudo systemctl is-active nginx

echo "🎉 Deployment complete!"
```

**Make executable:**

```bash
sudo chmod +x /opt/mrc-runs/deploy.sh
sudo chown mrcuser:www-data /opt/mrc-runs/deploy.sh
```

### Step 2: Configure Passwordless Sudo

```bash
# Allow mrcuser to restart services without password
sudo visudo

# Add at the end:
mrcuser ALL=(ALL) NOPASSWD: /bin/systemctl restart gunicorn
mrcuser ALL=(ALL) NOPASSWD: /bin/systemctl reload nginx
mrcuser ALL=(ALL) NOPASSWD: /bin/systemctl is-active gunicorn
mrcuser ALL=(ALL) NOPASSWD: /bin/systemctl is-active nginx

# Save and exit (Ctrl+X, Y, Enter)
```

### Step 3: Set Up GitHub Secrets

On GitHub:
1. Go to your repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"

**Add these secrets:**

| Name | Value |
|------|-------|
| `OCI_SSH_PRIVATE_KEY` | Content of `~/.ssh/oci_mrc_runs` (private key) |
| `OCI_HOST` | Your OCI instance public IP |
| `OCI_USER` | `ubuntu` (or `opc` for Oracle Linux) |

**To get private key content:**
```bash
cat ~/.ssh/oci_mrc_runs
# Copy entire content including BEGIN/END lines
```

### Step 4: Create GitHub Actions Workflow

In your repository, create:

**`.github/workflows/deploy.yml`**

```yaml
name: Deploy to OCI

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          python manage.py test runs

      - name: Run Django checks
        run: |
          python manage.py check --deploy

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - name: Deploy to OCI
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.OCI_HOST }}
          username: ${{ secrets.OCI_USER }}
          key: ${{ secrets.OCI_SSH_PRIVATE_KEY }}
          script: |
            sudo su - mrcuser -c '/opt/mrc-runs/deploy.sh'

      - name: Verify deployment
        run: |
          sleep 10
          curl -f -k https://${{ secrets.OCI_HOST }} || exit 1
          echo "✅ Deployment verified successfully!"
```

### Step 5: Test Deployment

```bash
# Commit and push the workflow file
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions deployment workflow"
git push origin main

# Watch the Actions tab on GitHub
# The workflow should:
# 1. Run tests
# 2. Deploy to OCI
# 3. Verify deployment
```

---

## Monitoring & Maintenance

### Application Logs

```bash
# View Gunicorn logs
sudo tail -f /opt/mrc-runs/logs/gunicorn-error.log
sudo tail -f /opt/mrc-runs/logs/gunicorn-access.log

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# View systemd journal for Gunicorn
sudo journalctl -u gunicorn -f
```

### Database Backups

Create automated daily backups:

```bash
# Create backup script
sudo nano /opt/mrc-runs/backup-db.sh
```

**Content:**

```bash
#!/bin/bash
BACKUP_DIR="/opt/mrc-runs/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="mrc_runs_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

# Dump database
export PGPASSWORD='YOUR_DB_PASSWORD'
pg_dump -U mrcadmin -h localhost mrc_runs | gzip > $BACKUP_DIR/$FILENAME

# Keep only last 7 days
find $BACKUP_DIR -name "mrc_runs_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $FILENAME"
```

**Make executable and schedule:**

```bash
sudo chmod +x /opt/mrc-runs/backup-db.sh

# Schedule daily at 2 AM
crontab -e

# Add line:
0 2 * * * /opt/mrc-runs/backup-db.sh >> /opt/mrc-runs/logs/backup.log 2>&1
```

### System Updates

```bash
# Weekly system update check
sudo apt update
sudo apt list --upgradable

# Apply updates
sudo apt upgrade -y

# Restart services if needed
sudo systemctl restart gunicorn nginx
```

---

## Troubleshooting

### Cannot SSH to Instance

**Check:**
1. Security List allows your IP on port 22
2. Instance is in "Running" state
3. Using correct username (`ubuntu` or `opc`)
4. SSH key permissions: `chmod 600 ~/.ssh/oci_mrc_runs`

```bash
# Verbose SSH for debugging
ssh -vvv -i ~/.ssh/oci_mrc_runs ubuntu@YOUR.IP
```

### Gunicorn Won't Start

```bash
# Check logs
sudo journalctl -u gunicorn -n 50

# Common issues:
# 1. Syntax error in .env file
# 2. Wrong path in service file
# 3. Permission issues on socket directory

# Test manually
sudo su - mrcuser
cd /opt/mrc-runs/app
source /opt/mrc-runs/venv/bin/activate
gunicorn --bind 0.0.0.0:8000 mrc_runs.wsgi:application
```

### Nginx 502 Bad Gateway

```bash
# Check if Gunicorn socket exists
ls -l /opt/mrc-runs/gunicorn.sock

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart both services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Static Files Not Loading

```bash
# Re-collect static files
sudo su - mrcuser
cd /opt/mrc-runs/app
source /opt/mrc-runs/venv/bin/activate
python manage.py collectstatic --noinput
exit

# Check permissions
ls -la /opt/mrc-runs/app/staticfiles/

# Restart Nginx
sudo systemctl restart nginx
```

### Database Connection Failed

```bash
# Test PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U mrcadmin -d mrc_runs -h localhost
# (You'll be prompted for password)

# Check credentials in .env
cat /opt/mrc-runs/.env
```

### Let's Encrypt Certificate Failed

**Common causes:**
1. Domain not pointing to instance IP
2. Port 80/443 not open in Security List
3. Nginx not configured correctly

```bash
# Check DNS
nslookup your-domain.com

# Test HTTP access
curl http://your-domain.com

# Check Nginx config
sudo nginx -t

# Try manual certificate
sudo certbot certonly --nginx -d your-domain.com
```

---

## Cost Summary

### OCI Always Free Resources
- Compute: **$0** (2 OCPU ARM, 12 GB RAM)
- Storage: **$0** (50 GB boot volume)
- Database: **$0** (self-hosted PostgreSQL)
- Networking: **$0** (up to 10 TB/month bandwidth)
- SSL Certificate: **$0** (Let's Encrypt)

### Optional Costs
- Domain name: **~$15/year**
- Additional storage: Paid if exceeding 200 GB total

**Total: $0/month + optional $15/year for domain**

---

## Next Steps

After successful deployment:

1. ✅ Test all application features
2. ✅ Set up monitoring (UptimeRobot, etc.)
3. ✅ Configure regular backups
4. ✅ Document your specific configuration
5. ✅ Consider implementing Issue #10 (HTMX) for better UX
6. ✅ Consider implementing Issue #9 (Social Auth) for easier login

## Support

- **OCI Documentation**: https://docs.oracle.com/en-us/iaas/
- **Django Deployment Checklist**: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
- **GitHub Actions Docs**: https://docs.github.com/en/actions

---

**Deployment Guide Version**: 1.0 (2025-01-27)
**Last Updated**: 2025-01-27
**Maintainer**: Claude Code
