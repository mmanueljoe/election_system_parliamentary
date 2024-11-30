# Base image for Nixpacks
FROM ghcr.io/railwayapp/nixpacks:ubuntu-1727136237

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-dev default-libmysqlclient-dev build-essential

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Set PATH for virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy project files
WORKDIR /election_app/
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose default Django port
EXPOSE 8000

# Default command to run the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
