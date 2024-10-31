# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the app files into the container
COPY . .

# Install Flask 
RUN pip install Flask

# Expose port 8080 for Flask
EXPOSE 8080

# Command to run the Flask app
CMD ["python", "app.py"]
