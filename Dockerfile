# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads/images

# Run database migrations
RUN alembic upgrade head

# Create initial admin user (if needed)
# Note: You might want to make these configurable via environment variables
ENV ADMIN_USERNAME=admin \
    ADMIN_PASSWORD=Admin123! \
    ADMIN_EMAIL=admin@example.com

# Add a script to initialize the database and start the application
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 