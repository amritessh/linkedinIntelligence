# scripts/test.sh
#!/bin/bash
echo "Running LinkedIntelligence Tests..."

cd backend
pytest tests/ -v --cov=. --cov-report=html