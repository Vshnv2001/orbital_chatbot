# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables for Python and watchfiles
# Ensures Python output is sent straight to the terminal without buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Force watchfiles (used by Uvicorn for --reload) to use polling.
# This is often crucial for detecting file changes within Docker volumes. [4][6]
ENV WATCHFILES_FORCE_POLLING=true

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# Ensure uvicorn[standard] and watchfiles are listed in your requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container.
# For hot reloading, you will mount your local code over this directory at runtime.
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn with reload enabled.
# Assumes your FastAPI app instance is named 'app' in a file named 'main.py'
# located in the root of the WORKDIR (i.e., /app/main.py).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
