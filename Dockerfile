# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    && apt-get clean

# Create a directory for the application
WORKDIR /app

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment and ensure it's on the PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application code
COPY . /election_app/

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["gunicorn", "election_system.wsgi:application", "--bind", "0.0.0.0:8000"]
