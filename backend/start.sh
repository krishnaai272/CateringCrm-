```sh
    #!/bin/bash
    
    # Exit immediately if a command exits with a non-zero status.
    set -e
    
    # Run the database migrations
    echo "--- Running database migrations ---"
    alembic -c alembic.ini upgrade head
    
    # Start the Uvicorn server
    echo "--- Starting Uvicorn server ---"
    exec uvicorn app.main:app --host 0.0.0.0 --port 10000