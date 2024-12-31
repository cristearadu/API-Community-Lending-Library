# PowerShell script for Windows users

# Function to cleanup on exit
function Cleanup {
    Write-Host "`n🛑 Interrupted by user" -ForegroundColor Red
    Write-Host "🛑 Stopping containers..." -ForegroundColor Red
    docker compose down
    Write-Host "✅ Containers stopped" -ForegroundColor Green
    exit 0
}

# Trap Ctrl+C
$null = Register-ObjectEvent -InputObject ([Console]) -EventName CancelKeyPress -Action { 
    Cleanup
}

Write-Host "Starting setup..." -ForegroundColor Green

# 1. Build Docker containers with no cache to ensure fresh build
Write-Host "`nBuilding Docker containers..." -ForegroundColor Green
docker compose build --no-cache

# 2. Start the containers in the background
Write-Host "`nStarting Docker containers..." -ForegroundColor Green
docker compose up -d

# 3. Wait for the application to be ready
Write-Host "`nWaiting for application to be ready..." -ForegroundColor Green
Start-Sleep -Seconds 5

# 4. Run tests inside the container
Write-Host "`nRunning tests..." -ForegroundColor Green
docker compose exec web pytest

# Check if tests passed
if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSetup completed successfully!" -ForegroundColor Green
    Write-Host "`nYou can now access the API at: http://localhost:8000"
    Write-Host "API documentation available at: http://localhost:8000/docs"
    
    # Show logs and follow them
    Write-Host "`nShowing application logs (Ctrl+C to exit):" -ForegroundColor Green
    docker compose logs -f
} else {
    Write-Host "`nTests failed! Please check the output above." -ForegroundColor Red
    docker compose down
    exit 1
} 