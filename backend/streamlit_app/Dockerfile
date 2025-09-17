FROM python:3.11-slim

WORKDIR /app

# Copy the backend requirements file
COPY ./backend/requirements.txt /app/

# Install the backend dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire backend folder into the container
COPY ./backend /app

# THIS IS THE NEW COMMAND SECTION
# It combines the migration and server start into one command,
# eliminating the need for a separate .sh file.
CMD ["sh", "-c", "alembic -c alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000"]
