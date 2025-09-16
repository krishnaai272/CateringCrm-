
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory IN THE CONTAINER to /app
# This is equivalent to your local "cd backend" command
WORKDIR /app

# Copy ONLY the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your application code into the container
# This will copy your 'app' folder, 'alembic' folder, etc., into /app
COPY . .

# THIS IS THE CORRECTED COMMAND
# It exactly matches what you run locally: "app.main:app"
# It also uses the port Render prefers.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]