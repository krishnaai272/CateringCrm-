FROM python:3.11-slim

# The working directory inside the container
WORKDIR /app

# Copy ALL files from the build context (the 'backend' folder) into the container's /app folder
COPY . .

# Install dependencies from the copied requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- THIS IS THE CRITICAL FIX ---
# Add the current directory (/app) to Python's search path.
# This guarantees that 'from app.models' will work.
ENV PYTHONPATH="${PYTHONPATH}:/app"

# This command will run alembic and then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000"]