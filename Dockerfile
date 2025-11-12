# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files and enable output flushing
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (if needed for Django or database clients)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for efficient caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose Django’s default port
EXPOSE 8000

# Run Django commands and start the server
# You can override this CMD in docker-compose if needed
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]