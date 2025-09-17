FROM python:3.11-slim

WORKDIR /app

# --- THIS IS THE FIX ---
# Copy the single requirements.txt from the project root
COPY ./requirements.txt /app/

# Install all dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire backend folder into the container
COPY ./backend /app/backend

# Copy the alembic.ini file into the container
COPY ./alembic.ini /app/alembic.ini

# The command to run your application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", "--app-dir", "/app/backend"]
