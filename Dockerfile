# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to improve performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory for the app
WORKDIR /election_app

# Create a virtual environment (venv) in the working directory
RUN python3 -m venv /opt/venv

# Activate the virtual environment and ensure it's on the PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the requirements file first to leverage Docker's cache
COPY requirements.txt /election_app/

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . /election_app/

# Collect static files during the build process
RUN python manage.py collectstatic --noinput

# Expose the port the app will run on
EXPOSE 4000

# Command to run the app with Gunicorn (Django production server)
CMD ["gunicorn", "election_system.wsgi:application", "--bind", "0.0.0.0:4000", "--workers", "3"]
