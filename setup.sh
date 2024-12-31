#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo -e "\n${RED}🛑 Interrupted by user${NC}"
    echo -e "${RED}🛑 Stopping containers...${NC}"
    docker compose down
    echo -e "${GREEN}✅ Containers stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

echo -e "${GREEN}Starting setup...${NC}"

# 1. Build Docker containers
echo -e "\n${GREEN}Building Docker containers...${NC}"
docker compose build

# 2. Start the containers in the background
echo -e "\n${GREEN}Starting Docker containers...${NC}"
docker compose up -d

# 3. Wait for the application to be ready
echo -e "\n${GREEN}Waiting for application to be ready...${NC}"
sleep 5  # Adjust this if needed

# 4. Run tests
echo -e "\n${GREEN}Running tests...${NC}"
pytest

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Setup completed successfully!${NC}"
    echo -e "\nYou can now access the API at: http://localhost:8000"
    echo -e "API documentation available at: http://localhost:8000/docs"
    
    # Show logs and follow them
    echo -e "\n${GREEN}Showing application logs (Ctrl+C to exit):${NC}"
    docker compose logs -f
else
    echo -e "\n${RED}Tests failed! Please check the output above.${NC}"
    exit 1
fi 