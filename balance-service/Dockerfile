# Use official Python image as the base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose the service port
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]
