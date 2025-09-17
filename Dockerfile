FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the entire backend folder into the container
COPY ./backend /app

# Install the backend dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# The command to run your application
# The working directory is now /app, which contains your 'app' folder
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
