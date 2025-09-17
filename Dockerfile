FROM python:3.11-slim

WORKDIR /app

# --- THIS IS THE CORRECTED LINE ---
# Copy the requirements file from the project root
COPY ./requirements.txt /app/

# Install the backend dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire backend folder into the container
COPY ./backend /app/backend

# Copy the alembic.ini file into the container
COPY ./alembic.ini /app/alembic.ini

# The command to run your application from the 'backend' subfolder
CMD ["sh", "-c", "alembic -c alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000"]