# Start N blockchain nodes with different ports and keys
# Usage: .\start_nodes.ps1 [NUMBER_OF_NODES]
# Default: 10 nodes if no parameter provided
# Node ports: 10000-1000N
# API ports: 11000-1100N

param(
    [int]$NumNodes = 10
)

# Validate input
if ($NumNodes -lt 1 -or $NumNodes -gt 100) {
    Write-Host "Error: Please provide a valid number of nodes (1-100)" -ForegroundColor Red
    Write-Host "Usage: .\start_nodes.ps1 [NUMBER_OF_NODES]"
    Write-Host "Example: .\start_nodes.ps1 5    # Start 5 nodes"
    Write-Host "Example: .\start_nodes.ps1      # Start 10 nodes (default)"
    exit 1
}

Write-Host "Starting $NumNodes blockchain nodes..." -ForegroundColor Green

# Set Python executable path
$pythonExe = "D:\proofwithquantumannealing\.winvenv\Scripts\python.exe"

# Kill any existing python processes for clean start
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Function to start a node
function Start-Node {
    param($nodeNum)
    
    $nodePort = 10000 + $nodeNum - 1
    $apiPort = 11000 + $nodeNum - 1
    $keyFile = "keys\node${nodeNum}_private_key.pem"
    
    # Use genesis key for node 1, or generate/use existing keys for other nodes
    if ($nodeNum -eq 1) {
        $keyFile = "keys\genesis_private_key.pem"
    } elseif (-not (Test-Path $keyFile)) {
        # If node key doesn't exist, use staker key as fallback
        if (Test-Path "keys\staker_private_key.pem") {
            $keyFile = "keys\staker_private_key.pem"
        } else {
            Write-Host "Warning: Key file $keyFile not found, using genesis key as fallback" -ForegroundColor Yellow
            $keyFile = "keys\genesis_private_key.pem"
        }
    }
    
    Write-Host "Starting Node $nodeNum - Port: $nodePort, API: $apiPort, Key: $keyFile"
    
    # Start the node process
    $processArgs = @(
        "run_node.py",
        "--ip", "localhost",
        "--node_port", $nodePort,
        "--api_port", $apiPort,
        "--key_file", $keyFile
    )
    
    $process = Start-Process -FilePath $pythonExe -ArgumentList $processArgs -WindowStyle Hidden -PassThru -RedirectStandardOutput "logs\node${nodeNum}.log" -RedirectStandardError "logs\node${nodeNum}_error.log"
    
    Write-Host "Node $nodeNum started with PID $($process.Id)"
    return $process
}

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Start all nodes
Write-Host "Launching $NumNodes nodes..." -ForegroundColor Cyan
$processes = @()
for ($i = 1; $i -le $NumNodes; $i++) {
    $process = Start-Node -nodeNum $i
    $processes += $process
    Start-Sleep -Seconds 1  # Small delay between node starts
}

Write-Host ""
Write-Host "All $NumNodes nodes started!" -ForegroundColor Green
Write-Host "Node ports: 10000-$(10000 + $NumNodes - 1)"
Write-Host "API ports: 11000-$(11000 + $NumNodes - 1)"
Write-Host "Logs: logs\node1.log - logs\node${NumNodes}.log"
Write-Host ""
Write-Host "Wait 10 seconds for nodes to initialize and connect..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "Checking node status..." -ForegroundColor Cyan
$activeNodes = 0
for ($i = 1; $i -le $NumNodes; $i++) {
    $apiPort = 11000 + $i - 1
    Write-Host -NoNewline "Node $i (API $apiPort): "
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$apiPort/api/v1/blockchain/" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "Running" -ForegroundColor Green
        $activeNodes++
    } catch {
        Write-Host "Not responding" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Network Summary:" -ForegroundColor Cyan
Write-Host "   Total Nodes Configured: $NumNodes"
Write-Host "   Active Nodes: $activeNodes"
$healthPct = [math]::Round(($activeNodes * 100) / $NumNodes, 1)
Write-Host "   Network Health: ${healthPct}%"

if ($activeNodes -eq $NumNodes) {
    Write-Host "   Perfect! All nodes are running successfully." -ForegroundColor Green
} elseif ($activeNodes -gt 0) {
    Write-Host "   Some nodes failed to start. Check logs for details." -ForegroundColor Yellow
} else {
    Write-Host "   No nodes are responding. Check configuration and logs." -ForegroundColor Red
}

Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "   Network analysis: $pythonExe analyze_forgers.py"
Write-Host "   Run transactions: $pythonExe test_transactions.py --count 10"
Write-Host "   Monitor network: $pythonExe analyze_forgers.py --watch 30"
Write-Host "   Stop all nodes: taskkill /f /im python.exe"
