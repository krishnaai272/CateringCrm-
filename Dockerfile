FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# --- File Copying ---
# First, copy the requirements file from your project root
COPY ./requirements.txt /app/

# Next, copy the alembic configuration file from your project root
COPY ./alembic.ini /app/

# Finally, copy your entire 'backend' folder (which contains your app and migrations)
COPY ./backend /app/backend

# --- Installation ---
# Install the Python libraries
RUN pip install --no-cache-dir -r /app/requirements.txt

# --- Execution ---
# This is the command that runs when the container starts.
# It uses 'sh -c' to run two commands in sequence:
# 1. Run the database migration, telling alembic where to find its config.
# 2. If the migration succeeds, start the Uvicorn server.
CMD ["sh", "-c", "alembic -c alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000 --app-dir /app/backend"]