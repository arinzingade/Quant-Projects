# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy only the requirements file first to leverage caching for dependencies
COPY requirements.txt . 

# Install dependencies early to take advantage of layer caching
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Install local dependencies
RUN pip install ./untrade-sdk

# Default command to run the application
CMD ["python", "main.py"]
