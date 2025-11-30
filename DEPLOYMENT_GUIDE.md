# 🚀 WildGaurd-Edge Public Deployment Guide

This guide covers deploying the WildGaurd-Edge web application publicly using multiple hosting options.

## Deployment Options

### Option 1: Heroku (Easiest for Beginners) ⭐ RECOMMENDED
### Option 2: Railway (Modern & Fast)
### Option 3: AWS (Scalable)
### Option 4: DigitalOcean (Affordable VPS)
### Option 5: Render (Free Tier Available)

---

## Option 1: Deploy to Heroku

### Prerequisites
- Heroku account (free at https://www.heroku.com)
- Heroku CLI installed
- Git installed

### Step 1: Install Heroku CLI
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
# Verify installation
heroku --version
```

### Step 2: Login to Heroku
```bash
heroku login
# Opens browser to login
```

### Step 3: Prepare Your App

Create `Procfile` in project root:
```
web: node node/server.js &
python scripts/app.py
```

Create `requirements.txt` (if not exists):
```bash
pip freeze > requirements.txt
```

Create `runtime.txt`:
```
python-3.13.7
nodejs-18.x
```

### Step 4: Create Heroku App
```bash
cd C:\Users\AADHITHAN\Downloads\WildGaurd-Edge

# Create new Heroku app
heroku create wildguard-edge-app

# Or use your custom name
heroku create your-custom-app-name
```

### Step 5: Deploy
```bash
# Push to Heroku
git push heroku main

# View logs
heroku logs --tail

# Open app in browser
heroku open
```

### Step 6: Configure Environment
```bash
# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=0
```

**Cost**: Free tier available, then $7-50/month
**Pros**: Easy, automatic HTTPS, free tier
**Cons**: No free tier for production apps (as of Nov 2022)

---

## Option 2: Railway (Modern & Fast) ⭐ HIGHLY RECOMMENDED

### Prerequisites
- Railway account (https://railway.app)
- GitHub connected to Railway

### Step 1: Connect GitHub to Railway
1. Go to https://railway.app
2. Sign up with GitHub
3. Authorize Railway to access repos

### Step 2: Deploy from GitHub
1. Click "New Project" → "Deploy from GitHub"
2. Select `WildGaurd-Edge` repository
3. Railway auto-detects Python + Node.js

### Step 3: Configure Environment
Railway dashboard > Environment:
```
PORT=5000
FLASK_ENV=production
NODE_ENV=production
```

### Step 4: Add Build & Start Commands
In Railway dashboard, set:
- **Build**: `npm install && pip install -r requirements.txt`
- **Start**: `node node/server.js & python scripts/app.py`

### Step 5: Deploy
Click "Deploy" - takes 2-3 minutes
Get public URL automatically

**Cost**: $5 credit free, then pay-as-you-go (~$5-20/month)
**Pros**: Very fast deployment, free credits, great UI
**Cons**: Costs money after free tier

---

## Option 3: AWS (Most Scalable)

### Step 1: Create AWS Account
- Go to https://aws.amazon.com
- Free tier available (1 year)

### Step 2: Launch EC2 Instance
```bash
1. EC2 Dashboard → Launch Instance
2. Select: Ubuntu 22.04 LTS (Free tier eligible)
3. Instance type: t2.micro (Free tier)
4. Create security group:
   - SSH: Port 22 (your IP)
   - HTTP: Port 80 (everywhere)
   - HTTPS: Port 443 (everywhere)
5. Create key pair (save .pem file)
6. Launch
```

### Step 3: Connect to Instance
```bash
# Get public IP from EC2 dashboard
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP

# Update system
sudo apt update && sudo apt upgrade -y
```

### Step 4: Install Dependencies
```bash
# Python
sudo apt install python3-pip python3-venv -y

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Git
sudo apt install git -y

# Nginx (reverse proxy)
sudo apt install nginx -y
```

### Step 5: Clone Repository
```bash
cd /home/ubuntu
git clone https://github.com/Aadthiyan/WildGaurd-Edge.git
cd WildGaurd-Edge

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Node dependencies
cd node
npm install
cd ..
```

### Step 6: Configure Nginx
Create `/etc/nginx/sites-available/wildguard`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/wildguard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Run Application (Using PM2)
```bash
# Install PM2 globally
sudo npm install -g pm2

# Create ecosystem config
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'node-server',
      script: 'node/server.js',
      instances: 1,
      exec_mode: 'cluster'
    },
    {
      name: 'flask-app',
      script: 'scripts/app.py',
      instances: 1
    }
  ]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

### Step 8: Add SSL Certificate (Free)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

**Cost**: Free for first year (t2.micro), ~$10/month after
**Pros**: Highly scalable, reliable, free tier
**Cons**: More complex setup

---

## Option 4: DigitalOcean (Affordable VPS)

### Step 1: Create DigitalOcean Account
- Go to https://www.digitalocean.com
- Sign up

### Step 2: Create Droplet
```
1. Click "Create" → "Droplets"
2. OS: Ubuntu 22.04 x64
3. Plan: Basic ($4-6/month)
4. Region: Nearest to you
5. Add SSH key
6. Create
```

### Step 3: SSH into Droplet
```bash
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y
```

### Step 4: Install Dependencies (Same as AWS Step 4-5)
```bash
# Python, Node.js, Git, Nginx
apt install python3-pip python3-venv nodejs git nginx -y

# Clone & setup
cd /root
git clone https://github.com/Aadthiyan/WildGaurd-Edge.git
cd WildGaurd-Edge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd node && npm install && cd ..
```

### Step 5: Configure & Deploy (Same as AWS Steps 6-8)

**Cost**: $4-6/month
**Pros**: Affordable, reliable, great documentation
**Cons**: Manual setup required

---

## Option 5: Render (Free Tier Available)

### Step 1: Sign Up
- Go to https://render.com
- Connect GitHub

### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your `WildGaurd-Edge` repo
3. Choose Python runtime

### Step 3: Configure
- **Build Command**: `pip install -r requirements.txt && cd node && npm install`
- **Start Command**: `gunicorn scripts.app:app`
- **Environment**: Add PORT=5000

### Step 4: Deploy
Click "Create Web Service"
Render deploys automatically

**Cost**: Free tier available (~$7/month for production)
**Pros**: Easy, free tier, GitHub integration
**Cons**: Free tier has limitations

---

## Quick Comparison Table

| Platform | Cost | Setup Difficulty | Best For |
|----------|------|------------------|----------|
| **Heroku** | $7-50/mo | Very Easy | Beginners |
| **Railway** | $5-20/mo | Easy | Modern devs |
| **AWS** | Free 1yr, then $10/mo | Medium | Scalability |
| **DigitalOcean** | $4-6/mo | Medium | Cost-conscious |
| **Render** | Free-$7/mo | Easy | Small projects |

---

## For Production Use: Recommended Setup

### Best Option: Railway + GitHub + Custom Domain

```bash
# Step 1: Push latest code to GitHub
git add .
git commit -m "Ready for public deployment"
git push origin main

# Step 2: Go to Railway.app
# - Connect your GitHub repo
# - Set environment variables
# - Deploy automatically

# Step 3: Add Custom Domain
# In Railway dashboard:
# 1. Project Settings → Domain
# 2. Add custom domain
# 3. Update DNS records at your domain registrar
```

---

## Custom Domain Setup

If deploying with custom domain (e.g., `wildguard.com`):

### Step 1: Register Domain
- Namecheap (~$10/year)
- GoDaddy (~$12/year)
- Google Domains (~$12/year)

### Step 2: Point to Hosting Provider
For Railway:
```
1. Get Railway domain: xxx.railway.app
2. Go to domain registrar
3. Update CNAME record: wildguard.com → xxx.railway.app
```

For AWS/DigitalOcean:
```
Update A record to server IP address
```

### Step 3: Enable HTTPS (Free)
- Railway: Automatic
- AWS/DigitalOcean: Use Let's Encrypt (Certbot)

---

## Environment Variables Needed

Create `.env` file or set in hosting platform:

```
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000
NODE_ENV=production
SECRET_KEY=your-secret-key-here
```

---

## Testing Deployment

After deployment:

```bash
# Test Flask app
curl https://your-domain.com/

# Test API
curl https://your-domain.com/api/model-info

# Test model server
curl https://your-domain.com:5001/api/health
```

---

## Monitoring & Maintenance

### View Logs
**Railway**: Dashboard → Logs
**AWS/DigitalOcean**: SSH in → `pm2 logs`
**Heroku**: `heroku logs --tail`

### Monitor Performance
- Railway: Built-in monitoring
- AWS CloudWatch: Metrics & alarms
- DigitalOcean: Simple metrics
- Render: Built-in monitoring

### Keep Updated
```bash
# Pull latest changes
git pull origin main

# Redeploy (platforms auto-redeploy on git push)
```

---

## Troubleshooting

### "Port already in use"
```bash
# Find process using port
lsof -i :5000
# Kill it
kill -9 PID
```

### "Connection refused"
Check if servers are running:
```bash
# Check Node server
curl localhost:5001/api/health

# Check Flask server
curl localhost:5000/
```

### "Model not found"
Ensure `edge-impulse-standalone.js` exists in `node/` folder

### Slow uploads
- Increase timeout in Nginx: `proxy_connect_timeout 300s;`
- Add file size limit: `client_max_body_size 100M;`

---

## Next Steps

### Immediate (Pick one platform):
1. Choose deployment platform
2. Follow steps above
3. Test publicly accessible URL

### Short-term:
1. Add custom domain
2. Enable HTTPS/SSL
3. Set up monitoring

### Long-term:
1. Set up CI/CD pipeline
2. Add database for storing results
3. Implement user authentication
4. Add analytics

---

## Cost Comparison (Annual)

| Platform | First Year | After Year 1 |
|----------|-----------|-------------|
| Railway | $60-240 | $60-240 |
| AWS Free Tier | $0 | $120+ |
| DigitalOcean | $48-72 | $48-72 |
| Heroku | $84-600 | $84-600 |
| Render | $0-84 | $84 |

---

## Support & Resources

- **Railway Docs**: https://docs.railway.app
- **AWS Docs**: https://docs.aws.amazon.com
- **DigitalOcean Community**: https://www.digitalocean.com/community
- **Heroku Docs**: https://devcenter.heroku.com
- **Render Docs**: https://render.com/docs

---

## Deployment Checklist

- [ ] Latest code pushed to GitHub
- [ ] `requirements.txt` up to date
- [ ] `node/package.json` up to date
- [ ] `.env` variables configured
- [ ] Domain name (optional) registered
- [ ] Platform account created
- [ ] App deployed successfully
- [ ] Both servers running (Node + Flask)
- [ ] Model inference working
- [ ] HTTPS enabled
- [ ] Monitoring set up
- [ ] Tested with public URL

Good luck with your deployment! 🚀
