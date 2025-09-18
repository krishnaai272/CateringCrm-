FROM python:3.11-slim

WORKDIR /app

# --- THIS IS THE FIX ---
# Instead of 'COPY . .', we will copy each item individually.
# This guarantees that the necessary folders are included.
COPY ./requirements.txt /app/
COPY ./alembic.ini /app/
COPY ./alembic /app/alembic/
COPY ./app /app/app/

# Install dependencies from the copied requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# This command will run when the container starts.
# It uses absolute paths to be foolproof.
CMD ["sh", "-c", "alembic -c /app/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000 --app-dir /app"]