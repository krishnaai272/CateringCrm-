FROM python:3.11-slim

# The working directory inside the container
WORKDIR /app

# Copy ALL files from the build context (the 'backend' folder) into the container's /app folder
COPY . .

# Install dependencies from the copied requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# This is the command that runs when the container starts.
# It runs alembic first, and then starts the server.
# Because the WORKDIR is /app, it will find alembic.ini correctly.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000"]
