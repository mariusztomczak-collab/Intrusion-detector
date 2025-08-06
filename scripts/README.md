# 🔧 Scripts Guide

This directory contains utility scripts for managing the Intrusion Detector application, organized by purpose and environment.

## 📁 Directory Structure

```
scripts/
├── 📖 README.md                    # This file - Scripts guide
├── 📁 deployment/                  # Deployment and production scripts
│   ├── 📄 start_app.sh           # Application startup script
│   ├── 📄 stop_app.sh            # Application shutdown script
│   ├── 📄 manage_app.sh          # Application management script
│   └── 📄 export_model.py        # Model export utility
├── 📁 development/                 # Development and testing scripts
│   └── 📄 create_sample_model.py # Sample model creation
└── 📁 maintenance/                 # Maintenance and utility scripts
    └── (future maintenance scripts)
```

## 🚀 Quick Access

For convenience, the main management scripts are symlinked to the project root:

- `start.sh` → `scripts/deployment/start_app.sh`
- `stop.sh` → `scripts/deployment/stop_app.sh`
- `manage.sh` → `scripts/deployment/manage_app.sh`

## 🚀 Deployment Scripts

### **start_app.sh**
Comprehensive application startup script with:
- **Dependency checks**: Docker, ports, environment
- **Service startup**: API, UI, Redis, Database
- **Health monitoring**: Service status verification
- **Error handling**: Graceful failure management
- **Colored output**: Clear status indicators

**Usage:**
```bash
# Start all services
./start.sh

# Start with custom environment
ENV_FILE=.env.production ./start.sh
```

**Features:**
- Automatic dependency installation
- Port availability checking
- Service health verification
- PID file management
- Logging and monitoring

### **stop_app.sh**
Application shutdown script with:
- **Graceful shutdown**: Proper service termination
- **Process cleanup**: PID file management
- **Resource cleanup**: Container and volume cleanup
- **Status reporting**: Shutdown confirmation

**Usage:**
```bash
# Stop all services
./stop.sh

# Force stop (if needed)
./stop.sh --force
```

**Features:**
- Graceful service termination
- Process cleanup
- Resource cleanup
- Status reporting

### **manage_app.sh**
Unified application management script with:
- **Start**: Start all services
- **Stop**: Stop all services
- **Restart**: Restart all services
- **Status**: Check service status
- **Logs**: View service logs

**Usage:**
```bash
# Start application
./manage.sh start

# Check status
./manage.sh status

# View logs
./manage.sh logs

# Stop application
./manage.sh stop

# Restart application
./manage.sh restart
```

**Features:**
- Unified interface for all operations
- Status monitoring
- Log management
- Error handling

### **export_model.py**
MLflow model export utility for distribution:
- **Model extraction**: Download from MLflow registry
- **Format conversion**: Export to joblib/pickle formats
- **Metadata generation**: Create model information files
- **Validation**: Test exported models

**Usage:**
```bash
# Export latest model
python scripts/deployment/export_model.py

# Export specific model version
python scripts/deployment/export_model.py --model-name intrusion_detector --version 2

# Export to custom directory
python scripts/deployment/export_model.py --output-dir ./models
```

**Features:**
- MLflow integration
- Multiple format support
- Metadata generation
- Model validation

## 🔧 Development Scripts

### **create_sample_model.py**
Sample model creation for testing:
- **Synthetic data**: Generate test datasets
- **Model training**: Create sample ML model
- **Preprocessor creation**: Generate data preprocessor
- **File export**: Save in multiple formats

**Usage:**
```bash
# Create sample model
python scripts/development/create_sample_model.py

# Create with custom parameters
python scripts/development/create_sample_model.py --samples 1000 --features 10
```

**Features:**
- Synthetic data generation
- Model training
- Preprocessor creation
- Multiple format export

## 🛠️ Maintenance Scripts

*Future maintenance scripts will be added here:*
- Database backup and restore
- Log rotation and cleanup
- Performance monitoring
- Security audits

## 📋 Script Categories

### **🚀 Deployment & Operations**
Scripts for deploying and managing the application in production.

**Key Scripts:**
- `start_app.sh` - Application startup
- `stop_app.sh` - Application shutdown
- `manage_app.sh` - Unified management
- `export_model.py` - Model distribution

**Use Cases:**
- Production deployment
- Service management
- Model distribution
- Environment setup

### **🔧 Development & Testing**
Scripts for development workflow and testing.

**Key Scripts:**
- `create_sample_model.py` - Sample model creation

**Use Cases:**
- Development setup
- Testing environment
- Model validation
- CI/CD pipeline

### **🔧 Maintenance & Utilities**
Scripts for maintenance and utility operations.

**Use Cases:**
- Database maintenance
- Log management
- Performance monitoring
- Security audits

## 🔧 Script Features

### **Common Features**
- **Error handling**: Graceful error management
- **Logging**: Comprehensive logging
- **Status reporting**: Clear status indicators
- **Configuration**: Environment-based configuration
- **Documentation**: Built-in help and usage

### **Security Features**
- **Input validation**: Parameter validation
- **Error sanitization**: Safe error messages
- **Permission checking**: File and directory permissions
- **Resource limits**: Memory and CPU limits

### **Monitoring Features**
- **Health checks**: Service health verification
- **Status monitoring**: Real-time status updates
- **Performance metrics**: Resource usage monitoring
- **Alerting**: Error and warning notifications

## 📊 Usage Examples

### **Development Workflow**
```bash
# Start development environment
./manage.sh start

# Create sample model for testing
python scripts/development/create_sample_model.py

# Run tests
pytest tests/

# Stop development environment
./manage.sh stop
```

### **Production Deployment**
```bash
# Export model for distribution
python scripts/deployment/export_model.py

# Deploy to production
./start.sh

# Monitor status
./manage.sh status

# View logs
./manage.sh logs
```

### **Maintenance Operations**
```bash
# Check system status
./manage.sh status

# Restart services
./manage.sh restart

# View detailed logs
./manage.sh logs --service api
```

## 🔒 Security Considerations

### **Script Security**
- Input validation and sanitization
- Error message sanitization
- File permission checking
- Resource limit enforcement

### **Production Security**
- Non-root execution
- Environment variable protection
- Log file security
- Network access control

## 📋 Script Checklist

### **Before Running Scripts**
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Permissions set correctly
- [ ] Resources available
- [ ] Backup completed (if needed)

### **After Running Scripts**
- [ ] Services started successfully
- [ ] Health checks passing
- [ ] Logs showing no errors
- [ ] Performance acceptable
- [ ] Security scan passed

## 🆘 Troubleshooting

### **Common Issues**
1. **Permission errors**: Check file permissions
2. **Port conflicts**: Verify port availability
3. **Environment issues**: Check environment variables
4. **Resource limits**: Monitor system resources

### **Debug Commands**
```bash
# Check script permissions
ls -la scripts/

# Validate environment
./manage.sh status

# View detailed logs
./manage.sh logs --verbose

# Test script syntax
bash -n scripts/deployment/start_app.sh
```

## 🤝 Contributing

### **Adding New Scripts**
1. Choose appropriate directory based on purpose
2. Follow naming conventions
3. Include error handling
4. Add documentation
5. Update this index

### **Script Standards**
- Use bash for shell scripts
- Include help and usage information
- Implement error handling
- Add logging and status reporting
- Follow security best practices

---

**🔧 Scripts for every need!** 🚀 