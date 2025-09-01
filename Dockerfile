# Dockerfile

# Start with an official, lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the file that lists the Python dependencies
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port that Gunicorn will run on
EXPOSE 5000

# The command to run your application using the Gunicorn server
# It runs the 'app' object from the 'app.py' file.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]