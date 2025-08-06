# ⚙️ Configuration Guide

This directory contains all configuration files for the Intrusion Detector application, organized by environment and purpose.

## 📁 Directory Structure

```
config/
├── 📖 README.md                    # This file - Configuration guide
├── 📁 production/                  # Production environment configurations
│   ├── 📄 docker-compose.prod.yml # Production Docker Compose
│   ├── 📄 Dockerfile.prod         # Production API Dockerfile
│   └── 📄 Dockerfile.ui           # Production UI Dockerfile
└── 📁 development/                 # Development environment configurations
    ├── 📄 docker-compose.yml      # Development Docker Compose
    ├── 📄 docker-compose-supabase.yml # Supabase local setup
    └── 📄 Dockerfile              # Development Dockerfile
```

## 🚀 Quick Access

For convenience, the main configuration files are symlinked to the project root:

- `docker-compose.prod.yml` → `config/production/docker-compose.prod.yml`
- `docker-compose.yml` → `config/development/docker-compose.yml`
- `Dockerfile.prod` → `config/production/Dockerfile.prod`
- `Dockerfile.ui` → `config/production/Dockerfile.ui`

## 🏭 Production Configuration

### **docker-compose.prod.yml**
Production Docker Compose configuration with:
- **API Service**: FastAPI backend with production settings
- **UI Service**: Gradio frontend
- **Redis**: Caching layer
- **PostgreSQL**: Database
- **Nginx**: Reverse proxy (optional)

**Key Features:**
- Health checks for all services
- Restart policies
- Volume mounts for model artifacts
- Environment variable configuration
- Security best practices

### **Dockerfile.prod**
Production Dockerfile for the API service:
- Based on Python 3.11-slim
- Multi-stage build for optimization
- Non-root user for security
- Health check configuration
- Model artifacts included

### **Dockerfile.ui**
Production Dockerfile for the UI service:
- Based on Python 3.11-slim
- Gradio interface configuration
- Health check configuration
- Non-root user for security

## 🔧 Development Configuration

### **docker-compose.yml**
Development Docker Compose configuration with:
- **API Service**: FastAPI backend with hot reload
- **MLflow**: Model tracking and registry
- **Redis**: Caching layer
- **PostgreSQL**: Database

**Key Features:**
- Volume mounts for development
- Hot reload enabled
- Debug mode enabled
- MLflow integration

### **docker-compose-supabase.yml**
Local Supabase setup for development:
- **Redis**: Caching layer
- **PostgreSQL**: Local database

### **Dockerfile**
Development Dockerfile:
- Includes development dependencies
- Hot reload configuration
- Debug tools

## 🔧 Environment Variables

### **Required Variables**
```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Redis Configuration
REDIS_URL=redis://host:port
```

### **Optional Variables**
```bash
# Application Configuration
APP_ENV=production|development
DEBUG=true|false
API_HOST=0.0.0.0
API_PORT=8000

# ML Configuration
MLFLOW_TRACKING_URI=local|http://mlflow:5000
MLFLOW_MODEL_NAME=intrusion_detector

# Security Configuration
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🚀 Usage Examples

### **Development Environment**
```bash
# Start development environment
docker-compose up -d

# Or use the management script
./manage.sh start
```

### **Production Environment**
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# Or use the deployment script
./scripts/deployment/start_app.sh
```

### **Custom Configuration**
```bash
# Use custom environment file
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

# Override specific variables
MLFLOW_TRACKING_URI=local docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security Considerations

### **Production Security**
- Non-root users in containers
- Read-only model artifact mounts
- Environment variable injection
- Health check monitoring
- Restart policies

### **Development Security**
- Local database isolation
- Development-specific configurations
- Debug mode controls
- Hot reload security

## 📊 Configuration Management

### **Environment-Specific Configs**
- **Development**: Optimized for development workflow
- **Production**: Optimized for security and performance
- **Staging**: Mirror of production for testing

### **Configuration Validation**
- Docker Compose syntax validation
- Environment variable validation
- Health check configuration
- Volume mount verification

## 🔄 Configuration Updates

### **Adding New Services**
1. Add service definition to appropriate docker-compose file
2. Update health checks
3. Configure environment variables
4. Update documentation

### **Modifying Existing Services**
1. Update service configuration
2. Test with local environment
3. Update documentation
4. Deploy to staging for validation

## 📋 Configuration Checklist

### **Before Deployment**
- [ ] Environment variables configured
- [ ] Health checks implemented
- [ ] Security measures in place
- [ ] Volume mounts configured
- [ ] Network configuration set
- [ ] Resource limits defined

### **After Deployment**
- [ ] Services starting correctly
- [ ] Health checks passing
- [ ] Logs showing no errors
- [ ] Performance metrics acceptable
- [ ] Security scan passed

## 🆘 Troubleshooting

### **Common Issues**
1. **Port conflicts**: Check port availability
2. **Volume mount errors**: Verify file permissions
3. **Environment variable issues**: Check variable names and values
4. **Health check failures**: Review service configuration

### **Debug Commands**
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs [service_name]

# Validate configuration
docker-compose config

# Check environment variables
docker-compose exec [service_name] env
```

---

**⚙️ Configuration management made simple!** 🔧 