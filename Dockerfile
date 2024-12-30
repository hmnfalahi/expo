# Use an official Python runtime as the base image
FROM python:3.12.7

# Set environment variables in key=value format
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies with retries in case of transient errors
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    || (sleep 10 && apt-get install -y --no-install-recommends gcc) \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/

# Copy the application code to the container
COPY . /app/

# Expose the port Django runs on
EXPOSE 8000

# Run the Django app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "expense_tracker.wsgi:application"]
