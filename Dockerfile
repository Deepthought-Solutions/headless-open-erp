# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Make port 8000 available to the world outside this container
EXPOSE 8000

# The entrypoint script will be created later and will run the migrations and then Gunicorn.
# For now, I'll set a placeholder command. I will replace this with the entrypoint script later.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "infrastructure.web.wsgi:app", "-b", "0.0.0.0:8000"]
