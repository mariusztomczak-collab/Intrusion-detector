# 🚀 Deployment Guide for Intrusion Detector

This guide explains how to deploy the Intrusion Detector application for end users without requiring MLflow.

## 📋 Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 80, 443, 8000, 7860, 6379, 5432 available

## 🔧 Step 1: Export Model (Developer Only)

Before distributing to end users, export the trained model:

```bash
# Start MLflow if not running
./start_app.sh

# Export model to artifacts directory
python scripts/export_model.py

# Verify exported files
ls -la artifacts/
```

You should see:
- `model.joblib` - Main model file
- `model.pkl` - Fallback model file  
- `preprocessor.joblib` - Data preprocessor
- `model_metadata.json` - Model information
- `README.md` - Usage instructions

## 📦 Step 2: Prepare Distribution Package

Create a distribution package for end users:

```bash
# Create distribution directory
mkdir intrusion-detector-dist
cd intrusion-detector-dist

# Copy application files
cp -r ../src/ .
cp ../run_unified_app.py .
cp ../requirements.txt .
cp ../docker-compose.prod.yml ./docker-compose.yml
cp ../Dockerfile.prod .
cp ../Dockerfile.ui .

# Copy model artifacts
cp -r ../artifacts/ .

# Copy this guide
cp ../DEPLOYMENT_GUIDE.md .

# Create .env template
cat > .env.template << EOF
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Database Configuration (optional, uses built-in PostgreSQL by default)
# DATABASE_URL=postgresql://user:password@host:port/database

# Redis Configuration (optional, uses built-in Redis by default)
# REDIS_URL=redis://host:port
EOF

# Create startup script
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Intrusion Detector..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please copy .env.template to .env and configure your settings."
    exit 1
fi

# Start services
docker-compose up -d

echo "✅ Application started!"
echo "🌐 UI: http://localhost:7860"
echo "🔌 API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
EOF

chmod +x start.sh

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Intrusion Detector..."
docker-compose down
echo "✅ Application stopped!"
EOF

chmod +x stop.sh

# Create status script
cat > status.sh << 'EOF'
#!/bin/bash
echo "📊 Intrusion Detector Status:"
docker-compose ps
echo ""
echo "🔍 Service Health:"
curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "API not responding"
EOF

chmod +x status.sh
```

## 🎯 Step 3: End User Deployment

### Option A: Docker Compose (Recommended)

1. **Extract the distribution package**
   ```bash
   tar -xzf intrusion-detector-dist.tar.gz
   cd intrusion-detector-dist
   ```

2. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your Supabase credentials
   nano .env
   ```

3. **Start the application**
   ```bash
   ./start.sh
   ```

4. **Access the application**
   - Web UI: http://localhost:7860
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option B: Manual Installation

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_KEY="your_supabase_anon_key"
   export MLFLOW_TRACKING_URI="local"
   ```

3. **Start services manually**
   ```bash
   # Start Redis
   redis-server &
   
   # Start PostgreSQL (if not using external)
   # ... PostgreSQL setup ...
   
   # Start API
   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
   
   # Start UI
   python run_unified_app.py &
   ```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | Required |
| `SUPABASE_KEY` | Your Supabase anon key | Required |
| `MLFLOW_TRACKING_URI` | MLflow URI (use "local" for end users) | `local` |
| `APP_ENV` | Application environment | `production` |
| `DEBUG` | Enable debug mode | `false` |

### Port Configuration

| Service | Port | Description |
|---------|------|-------------|
| UI | 7860 | Gradio web interface |
| API | 8000 | FastAPI backend |
| Redis | 6379 | Cache layer |
| PostgreSQL | 5432 | Database |
| Nginx | 80/443 | Reverse proxy |

## 🔍 Monitoring and Troubleshooting

### Check Application Status
```bash
./status.sh
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs ui
```

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# UI health
curl http://localhost:7860
```

### Common Issues

1. **Model not loading**
   - Verify `artifacts/` directory contains model files
   - Check application logs for model loading errors

2. **Database connection issues**
   - Verify Supabase credentials in `.env`
   - Check network connectivity

3. **Port conflicts**
   - Change ports in `docker-compose.yml`
   - Stop conflicting services

## 🔒 Security Considerations

1. **Environment Variables**
   - Never commit `.env` files to version control
   - Use strong, unique passwords
   - Rotate credentials regularly

2. **Network Security**
   - Use HTTPS in production
   - Configure firewall rules
   - Limit access to necessary ports only

3. **Model Security**
   - Keep model files secure
   - Don't expose model files publicly
   - Consider model encryption for sensitive deployments

## 📈 Production Deployment

For production environments:

1. **Use a reverse proxy (Nginx)**
2. **Enable SSL/TLS certificates**
3. **Set up monitoring and logging**
4. **Configure backups for database**
5. **Use external database and Redis if needed**
6. **Set up CI/CD pipeline for updates**

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Stop current version
./stop.sh

# Backup data
docker-compose exec db pg_dump -U postgres intrusion_detector > backup.sql

# Update code and restart
git pull  # or copy new files
./start.sh
```

### Updating the Model
1. Export new model using `scripts/export_model.py`
2. Replace `artifacts/` directory
3. Restart application

## 📞 Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Verify configuration in `.env`
3. Test individual services
4. Check this guide for common solutions

---

**Note**: This deployment guide assumes you have the necessary permissions and infrastructure to run Docker containers. For enterprise deployments, consult with your IT team for specific requirements. 