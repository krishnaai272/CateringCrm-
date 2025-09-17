FROM python:3.11-slim

# The working directory inside the container
WORKDIR /app

# Copy all files from the current folder (backend) into the container
COPY . .

# Install dependencies from the copied requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# The command to run when the container starts
# Runs migrations, then starts the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000"]