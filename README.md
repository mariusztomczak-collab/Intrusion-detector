# 🛡️ Intrusion Detector

A machine learning-based network intrusion detection system with a modern web interface, built with FastAPI, Gradio, and Supabase.

[![CI/CD](https://github.com/mariusztomczak-collab/Intrusion-detector/workflows/Pull%20Request%20CI%2FCD/badge.svg)](https://github.com/mariusztomczak-collab/Intrusion-detector/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Supabase account

### Development Setup
```bash
# Clone the repository
git clone https://github.com/mariusztomczak-collab/Intrusion-detector.git
cd Intrusion-detector

# Install dependencies
pip install -e ".[dev]"

# Start development environment
./manage.sh start

# Access the application
# UI: http://localhost:7860
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Production Deployment
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Or follow the detailed deployment guide
# See: docs/deployment/DEPLOYMENT_GUIDE.md
```

## 📁 Project Structure

```
intrusion-detector/
├── 📁 src/                    # Application source code
│   ├── 📁 api/               # FastAPI backend
│   ├── 📁 ui/                # Gradio frontend
│   ├── 📁 ml/                # Machine learning components
│   └── 📁 core/              # Core utilities
├── 📁 tests/                 # Test suite
├── 📁 docs/                  # Documentation
│   ├── 📁 deployment/        # Deployment guides
│   ├── 📁 development/       # Development guides
│   ├── 📁 api/              # API documentation
│   └── 📁 architecture/     # Architecture docs
├── 📁 config/               # Configuration files
│   ├── 📁 production/       # Production configs
│   └── 📁 development/      # Development configs
├── 📁 scripts/              # Utility scripts
│   ├── 📁 deployment/       # Deployment scripts
│   ├── 📁 development/      # Development scripts
│   └── 📁 maintenance/      # Maintenance scripts
├── 📁 database/             # Database files
│   └── 📁 migrations/       # SQL migrations
├── 📁 artifacts/            # ML model files
├── 📁 supabase/             # Supabase configuration
└── 📁 .github/              # GitHub Actions workflows
```

## 🏗️ Architecture

### Technology Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Gradio (Python)
- **Database**: PostgreSQL + Supabase
- **Authentication**: Supabase Auth
- **ML Framework**: Scikit-learn
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

### Key Features
- 🔐 **Secure Authentication** with Supabase
- 🤖 **ML-Powered Detection** using Logistic Regression
- 📊 **Real-time Analysis** with caching
- 🐳 **Containerized Deployment** with Docker
- 🔄 **CI/CD Pipeline** with automated testing
- 📈 **Comprehensive Monitoring** with health checks

## 📚 Documentation

### 📖 Guides
- **[Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[Model Distribution](docs/deployment/MODEL_DISTRIBUTION_SOLUTION.md)** - ML model distribution solution
- **[Development Guide](docs/development/)** - Development setup and guidelines
- **[API Documentation](docs/api/)** - API design and implementation
- **[Architecture](docs/architecture/)** - System architecture and design

### 🔧 Configuration
- **[Production Config](config/production/)** - Production environment configuration
- **[Development Config](config/development/)** - Development environment configuration

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=src --cov-report=html
```

### CI/CD Pipeline
The project includes a comprehensive CI/CD pipeline with:
- ✅ Code linting (Black, isort, flake8, mypy)
- ✅ Unit and integration tests
- ✅ Security scanning (Bandit, Safety)
- ✅ Docker image building
- ✅ Automated PR status comments

## 🚀 Deployment

### Development
```bash
# Start all services
./manage.sh start

# Check status
./manage.sh status

# Stop services
./manage.sh stop
```

### Production
```bash
# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or use the deployment scripts
./scripts/deployment/start_app.sh
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Optional
MLFLOW_TRACKING_URI=local  # Use local models
APP_ENV=production
DEBUG=false
```

### Model Configuration
The system supports multiple model loading strategies:
1. **MLflow Model Registry** (for developers)
2. **Local joblib files** (for end users)
3. **Fallback pickle files** (backup)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Check the [docs/](docs/) directory
- 🐛 **Issues**: Report bugs via [GitHub Issues](https://github.com/mariusztomczak-collab/Intrusion-detector/issues)
- 💬 **Discussions**: Join the [GitHub Discussions](https://github.com/mariusztomczak-collab/Intrusion-detector/discussions)

## 🏆 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [Gradio](https://gradio.app/)
- Authentication by [Supabase](https://supabase.com/)
- ML framework: [Scikit-learn](https://scikit-learn.org/)

---

**Made with ❤️ for network security**
