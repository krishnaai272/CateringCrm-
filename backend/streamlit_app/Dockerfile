FROM python:3.11-slim

WORKDIR /app

# Copy all files from the backend folder into the container's /app folder
COPY . .

# Install dependencies from the copied requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# This command will run alembic and then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000"]
