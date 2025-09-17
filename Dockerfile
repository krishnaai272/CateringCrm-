FROM python:3.11-slim

WORKDIR /app

# Copy the requirements file for the backend first
COPY ./backend/requirements.txt /app/

# Install the backend dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire backend folder into the container
# This is where start.sh, alembic.ini, and the 'app' folder are located
COPY ./backend /app

# --- THIS IS THE CORRECTED PART ---
# Make the start.sh script executable at its correct new path
RUN chmod +x /app/start.sh

# The command to run when the container starts
# We now run the script from its correct path
CMD ["/app/start.sh"]