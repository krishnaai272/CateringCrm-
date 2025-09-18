FROM python:3.11-slim

# The working directory inside the container
WORKDIR /app

# Copy ALL files from the build context (the 'backend' folder) into the container's /app folder
COPY . .

# Install dependencies from the copied requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- THIS IS THE CRITICAL DEBUGGING COMMAND ---
# It will first print a detailed, recursive list of ALL files and folders in the /app directory.
# Then, it will attempt to run our original command.
CMD ["sh", "-c", "echo '--- Listing contents of /app directory ---'; ls -laR /app; echo '--- Attempting to run migrations ---'; alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000"]