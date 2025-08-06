# 🚀 Production Deployment Guide

Complete guide to deploy your AI ChatBot to production with multiple hosting options.

## 📋 Prerequisites

### Required Tools
- **Docker** & **Docker Compose** (for containerization)
- **Git** (for version control)
- **OpenAI API Key** (for AI functionality)
- **Domain name** (optional, for custom domains)

### Recommended System Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 20GB+ SSD
- **Network**: Stable internet connection

---

## 🐳 **Option 1: Docker Deployment (Recommended)**

### Quick Start
```bash
# 1. Clone and setup
git clone <your-repo>
cd AIChatBot

# 2. Configure environment
cp env.production.template .env
# Edit .env with your settings

# 3. Deploy with one command
chmod +x deploy.sh
./deploy.sh deploy
```

### Manual Docker Deployment
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ☁️ **Option 2: AWS Deployment**

### **A. AWS EC2 + Docker**

#### Step 1: Launch EC2 Instance
```bash
# Instance recommendations:
# - Instance Type: t3.medium or larger
# - OS: Ubuntu 22.04 LTS
# - Storage: 20GB+ SSD
# - Security Group: Allow ports 22, 80, 443, 8000
```

#### Step 2: Setup EC2
```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again
exit
```

#### Step 3: Deploy Application
```bash
# Clone your repository
git clone <your-repo>
cd AIChatBot

# Configure environment
cp env.production.template .env
nano .env  # Edit with your settings

# Deploy
./deploy.sh deploy
```

### **B. AWS ECS (Container Service)**

#### Step 1: Create Task Definition
```json
{
  "family": "chatbot-backend",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "chatbot-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/chatbot-backend",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "OPENAI_API_KEY", "value": "your-key"}
      ]
    }
  ]
}
```

#### Step 2: Create ECS Service
```bash
# Create cluster
aws ecs create-cluster --cluster-name chatbot-cluster

# Create service
aws ecs create-service \
  --cluster chatbot-cluster \
  --service-name chatbot-backend \
  --task-definition chatbot-backend \
  --desired-count 1 \
  --launch-type FARGATE
```

---

## 🔵 **Option 3: Digital Ocean Deployment**

### **A. Digital Ocean Droplet**

#### Step 1: Create Droplet
- **Size**: 2GB RAM, 1 CPU ($12/month)
- **Image**: Ubuntu 22.04
- **Datacenter**: Choose nearest to your users

#### Step 2: Setup Droplet
```bash
# SSH into droplet
ssh root@your-droplet-ip

# Run the setup script
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone <your-repo>
cd AIChatBot
cp env.production.template .env
# Edit .env file
./deploy.sh deploy
```

### **B. Digital Ocean App Platform**

#### Create app.yaml
```yaml
name: ai-chatbot
services:
- name: backend
  source_dir: /
  dockerfile_path: Dockerfile.backend
  http_port: 8000
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: OPENAI_API_KEY
    value: ${OPENAI_API_KEY}
    
- name: frontend
  source_dir: /
  dockerfile_path: Dockerfile.frontend
  http_port: 80
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
```

---

## 🌐 **Option 4: Google Cloud Platform**

### **A. Google Compute Engine**
```bash
# Create VM instance
gcloud compute instances create chatbot-vm \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server

# SSH and setup
gcloud compute ssh chatbot-vm
# Follow same Docker setup as EC2
```

### **B. Google Cloud Run**
```bash
# Build and push to Google Container Registry
docker build -f Dockerfile.backend -t gcr.io/your-project/chatbot-backend .
docker push gcr.io/your-project/chatbot-backend

# Deploy to Cloud Run
gcloud run deploy chatbot-backend \
  --image gcr.io/your-project/chatbot-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🔮 **Option 5: Heroku Deployment**

### Create heroku.yml
```yaml
build:
  docker:
    backend: Dockerfile.backend
    frontend: Dockerfile.frontend
run:
  backend: uvicorn backend.server:app --host 0.0.0.0 --port $PORT
```

### Deploy to Heroku
```bash
# Install Heroku CLI
# Create Heroku apps
heroku create your-chatbot-backend
heroku create your-chatbot-frontend

# Set environment variables
heroku config:set OPENAI_API_KEY=your-key --app your-chatbot-backend

# Deploy
git push heroku main
```

---

## 🔒 **Option 6: Security Enhancements**

### SSL/HTTPS Setup with Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration
```bash
# UFW firewall setup
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
```

---

## 📊 **Monitoring & Logging**

### Add Monitoring Stack
```yaml
# Add to docker-compose.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Logging Setup
```bash
# Centralized logging with ELK stack
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  elasticsearch:7.14.0
```

---

## 💰 **Cost Estimates**

### Monthly Hosting Costs

| **Provider** | **Configuration** | **Cost/Month** |
|--------------|-------------------|----------------|
| **Digital Ocean** | 2GB Droplet | $12 |
| **AWS EC2** | t3.medium | $30-40 |
| **Google Cloud** | e2-medium | $25-35 |
| **Heroku** | Hobby tier | $14-28 |
| **Linode** | 2GB instance | $10 |

### Additional Costs
- **Domain**: $10-15/year
- **SSL Certificate**: Free (Let's Encrypt)
- **OpenAI API**: Pay-per-use
- **Storage**: $1-5/month
- **Monitoring**: Free (basic) or $10-20/month (advanced)

---

## 🚀 **Production Checklist**

### Before Deployment
- [ ] Configure environment variables
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test all functionality

### Security Checklist
- [ ] Enable HTTPS
- [ ] Set strong passwords
- [ ] Configure rate limiting
- [ ] Enable CORS properly
- [ ] Set up fail2ban
- [ ] Regular security updates

### Performance Optimization
- [ ] Enable gzip compression
- [ ] Set up CDN for static assets
- [ ] Configure database connection pooling
- [ ] Set up Redis caching
- [ ] Monitor resource usage

---

## 🆘 **Troubleshooting**

### Common Issues

**Backend not starting:**
```bash
# Check logs
docker-compose logs backend

# Common fixes:
# 1. Check OPENAI_API_KEY
# 2. Verify port 8000 is available
# 3. Check Docker memory limits
```

**Frontend not loading:**
```bash
# Check nginx configuration
docker-compose logs frontend

# Verify API connection
curl http://localhost:8000/
```

**Database connection issues:**
```bash
# Check database logs
docker-compose logs postgres

# Verify credentials in .env file
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check disk space
df -h

# Monitor logs
tail -f logs/app.log
```

---

## 📞 **Support & Maintenance**

### Regular Maintenance Tasks
- Update Docker images monthly
- Backup database weekly
- Monitor SSL certificate expiry
- Review security logs
- Update dependencies quarterly

### Backup Strategy
```bash
# Backup database
docker-compose exec postgres pg_dump -U chatbot chatbot > backup.sql

# Backup ChromaDB
tar -czf chroma_backup.tar.gz chroma_db/

# Backup configuration
tar -czf config_backup.tar.gz .env docker-compose.yml
```

---

## 🎯 **Recommended Deployment Path**

For beginners: **Digital Ocean Droplet** ($12/month)
For scaling: **AWS EC2 + RDS** ($40-60/month)
For enterprise: **Kubernetes + AWS EKS** ($100+/month)

Choose based on your traffic, budget, and technical expertise level. 