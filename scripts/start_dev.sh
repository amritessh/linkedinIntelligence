# scripts/start_dev.sh
#!/bin/bash
echo "Starting LinkedIntelligence Development Environment..."

# Start databases
docker-compose up -d

# Wait for databases to be ready
sleep 5

# Run database migrations
cd backend
alembic upgrade head

# Start the API server
python main.py