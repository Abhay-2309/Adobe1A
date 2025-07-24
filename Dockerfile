# Stage 1: Use a standard Python image as the base
# Using --platform is a good practice as suggested by the hackathon rules
FROM --platform=linux/amd64 python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install the Python dependencies
# --no-cache-dir makes the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY src/ ./src/

# Copy the input directory (optional, but good for self-contained testing)
# In the actual judging, they will mount their own input folder
COPY input/ ./input/

# Specify the command to run when the container starts
# We use the -m flag to run the src/main.py as a module, which solves import issues
CMD ["python", "-m", "src.main"]