FROM python:3.11-slim

WORKDIR /app

# Copy the backend requirements file
COPY backend/requirements.txt /app/

# Install the backend dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire backend folder into the container at /app
COPY backend/ /app/

# --- THIS IS THE CRITICAL FIX ---
# Add the /app directory to Python's search path.
# Now, any script can import from 'app' (e.g., 'from app.models import Base')
ENV PYTHONPATH="${PYTHONPATH}:/app"

# This command will run alembic and then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000"]