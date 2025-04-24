# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libpq-dev \
    python3-dev \
    pkg-config \
    build-essential \
    mariadb-client \
    libmariadb-dev

# Set work directory
WORKDIR /app

# Copy project
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run Gunicorn
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
