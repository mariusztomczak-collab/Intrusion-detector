# Network Intrusion Detection System

A machine learning-based system for detecting malicious network traffic using the KD-NSL dataset.

## Repository Structure

```
intrusion-detector/
├── app/                    # Application code
│   ├── api/               # FastAPI application
│   │   ├── endpoints/     # API endpoints
│   │   ├── middleware/    # Custom middleware
│   │   └── schemas/       # Pydantic models
│   ├── core/              # Core functionality
│   │   ├── config/        # Configuration
│   │   └── supabase/      # Supabase client
│   └── ml/                # ML pipeline
│       ├── models/        # Model definitions
│       ├── preprocessing/ # Data preprocessing
│       └── training/      # Model training
├── data/                  # Data directory
│   ├── raw/              # Raw data files
│   ├── processed/        # Processed data files
│   └── test/             # Test data
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   └── db/               # Database documentation
├── notebooks/            # Jupyter notebooks
├── scripts/              # Utility scripts
├── supabase/            # Supabase configuration
│   └── migrations/      # Database migrations
├── tests/               # Test files
│   ├── api/            # API tests
│   ├── ml/             # ML pipeline tests
│   └── integration/    # Integration tests
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore file
├── docker-compose.yml  # Docker compose configuration
├── Dockerfile          # Docker configuration
├── Makefile           # Build and development commands
├── pyproject.toml     # Python project configuration
├── README.md          # This file
└── requirements.txt    # Python dependencies
```

## Setup

1. Create and activate a virtual environment:
  ```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the services:
```bash
# Start MLflow server
mlflow server --host 0.0.0.0 --port 5000

# Start FastAPI application
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Development

- Run tests: `make test`
- Format code: `make format`
- Lint code: `make lint`

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## MLflow

The MLflow server is available at:
- MLflow UI: http://localhost:5000

## License

This project is licensed under the MIT License - see the LICENSE file for details.
