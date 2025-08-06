from setuptools import setup, find_packages

setup(
    name="intrusion-detector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn",
        "joblib",
        "mlflow",
        "fastapi",
        "uvicorn",
        "python-multipart",
        "redis",
        "fastapi-cache2[redis]",
    ],
) 