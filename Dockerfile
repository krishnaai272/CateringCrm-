FROM python:3.11-slim

WORKDIR /app

# Copy the requirements file first for caching
COPY ./backend/requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire backend folder into the container
# This includes the new start.sh script
COPY ./backend /app

# Make the start.sh script executable
RUN chmod +x /app/start.sh

# The command to run when the container starts
# This will now run our script
CMD ["/app/start.sh"]