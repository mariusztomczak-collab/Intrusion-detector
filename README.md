# Intrusion Detection Web App

A lightweight, Dockerized web application for classifying network traffic as **malicious** or **normal** using a trained machine learning model based on the KD-NSL dataset. Designed for law enforcement professionals, it offers both real-time and batch classification, a simple UI, and REST API endpoints.

---

## Table of Contents

1. [Project Description](#project-description)  
2. [Tech Stack](#tech-stack)  
3. [Getting Started Locally](#getting-started-locally)  
4. [Available Scripts](#available-scripts)  
5. [Project Scope](#project-scope)  
6. [Project Status](#project-status)  
7. [License](#license)

---

## Project Description

This web-based platform enables users to detect malicious network activity using a pre-trained ML model. The UI is tailored for ease-of-use by non-technical users and offers immediate feedback on uploaded data. It supports:

- Real-time single request classification via UI (Gradio).
- Batch classification through REST API (FastAPI).
- Local deployment with Docker for secure offline usage.

Use cases include automated event analysis in law enforcement and cybersecurity auditing.

---

## Tech Stack

### Frontend
- **Gradio**: Simple, Python-native UI framework.

### Backend
- **FastAPI**: Fast, type-checked REST API framework.
- **Pydantic**: Input validation and schema definition.
- **Authentication**: HTTP Basic Auth or JWT (local user management).

### ML Model
- Trained offline and integrated as a microservice or local callable.
- Formats: `.pkl`, `.joblib`, or `.onnx`.

### Monitoring
- **MLflow**: Internal tracking for experiments and model performance metrics (not exposed to end-users).

### Database
- **PostgreSQL**: Stores user history, requests/responses, and metadata.

### Containerization & DevOps
- **Docker + Docker Compose**: Local development and service isolation.
- **GitHub Actions**: CI/CD for testing and deployment.
- **DigitalOcean**: Hosting via Docker Droplet or App Platform.

---

## Getting Started Locally

### Prerequisites
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Steps

```bash
# Clone the repository
git clone https://github.com/your-username/intrusion-detector.git
cd intrusion-detector

# Start the services
docker-compose up --build
```

## Development

- Use `black` for code formatting
- Use `flake8` for linting
- Use `