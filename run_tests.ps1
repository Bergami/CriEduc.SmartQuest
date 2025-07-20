# SmartQuest Test Runner
# PowerShell script to run all tests with proper configuration

param(
    [switch]$Unit,
    [switch]$Integration,
    [switch]$Coverage,
    [switch]$Verbose,
    [switch]$Fast,
    [switch]$NoCov,
    [switch]$Help
)

# Help function
function Show-Help {
    Write-Host "SmartQuest Test Runner - PowerShell Edition" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\run_tests.ps1 [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  -Unit        Run only unit tests"
    Write-Host "  -Integration Run only integration tests"
    Write-Host "  -Coverage    Generate coverage report"
    Write-Host "  -Verbose     Enable verbose output"
    Write-Host "  -Fast        Skip slow tests"
    Write-Host "  -NoCov       Skip coverage collection"
    Write-Host "  -Help        Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Magenta
    Write-Host "  .\run_tests.ps1                    # Run all tests"
    Write-Host "  .\run_tests.ps1 -Unit              # Run only unit tests"
    Write-Host "  .\run_tests.ps1 -Integration       # Run only integration tests"
    Write-Host "  .\run_tests.ps1 -Coverage          # Run tests with coverage report"
    Write-Host "  .\run_tests.ps1 -Fast              # Skip slow tests"
    Write-Host "  .\run_tests.ps1 -Verbose -Coverage # Verbose output with coverage"
    Write-Host ""
}

# Show help if requested
if ($Help) {
    Show-Help
    exit 0
}

# Function to run command with proper output handling
function Invoke-TestCommand {
    param(
        [string]$Command,
        [string]$Description
    )
    
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Blue
    Write-Host "🔄 $Description" -ForegroundColor Yellow
    Write-Host "=" * 60 -ForegroundColor Blue
    
    try {
        Invoke-Expression $Command
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description completed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $Description failed with exit code $LASTEXITCODE" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error running command: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host "🚀 SmartQuest Test Runner" -ForegroundColor Green
Write-Host "📁 Project Root: $(Get-Location)" -ForegroundColor Cyan
Write-Host "🐍 Python Version: $(python --version)" -ForegroundColor Cyan

# Build pytest command
$baseCommand = @("python", "-m", "pytest")

# Add coverage if not disabled
if (-not $NoCov) {
    $baseCommand += @(
        "--cov=app",
        "--cov-report=html:tests/coverage/html",
        "--cov-report=xml:tests/coverage/coverage.xml",
        "--cov-report=term-missing",
        "--cov-branch"
    )
}

# Add verbosity
if ($Verbose) {
    $baseCommand += "-v"
} else {
    $baseCommand += "-q"
}

# Add test type filters
if ($Unit) {
    $baseCommand += @("-m", "unit")
} elseif ($Integration) {
    $baseCommand += @("-m", "integration")
}

# Skip slow tests if requested
if ($Fast) {
    $baseCommand += @("-m", "not slow")
}

# Run tests
$success = $true

if ($Unit) {
    Write-Host "🧪 Running Unit Tests..." -ForegroundColor Magenta
    $unitCommand = ($baseCommand + @("tests/unit/")) -join " "
    $success = $success -and (Invoke-TestCommand -Command $unitCommand -Description "Unit Tests")
    
} elseif ($Integration) {
    Write-Host "🔗 Running Integration Tests..." -ForegroundColor Magenta
    $integrationCommand = ($baseCommand + @("tests/integration/")) -join " "
    $success = $success -and (Invoke-TestCommand -Command $integrationCommand -Description "Integration Tests")
    
} else {
    Write-Host "🧪 Running All Tests..." -ForegroundColor Magenta
    $allCommand = ($baseCommand + @("tests/")) -join " "
    $success = $success -and (Invoke-TestCommand -Command $allCommand -Description "All Tests")
}

# Generate coverage report if requested
if ($Coverage -and -not $NoCov) {
    Write-Host "📊 Generating Coverage Report..." -ForegroundColor Magenta
    $coverageCommand = "python -m coverage html"
    Invoke-TestCommand -Command $coverageCommand -Description "Coverage Report Generation"
    
    # Check if coverage report exists
    $coverageFile = Join-Path -Path (Get-Location) -ChildPath "tests\coverage\html\index.html"
    if (Test-Path $coverageFile) {
        Write-Host "📈 Coverage report generated: $coverageFile" -ForegroundColor Green
        
        # Ask if user wants to open the report
        $openReport = Read-Host "Do you want to open the coverage report? (y/n)"
        if ($openReport -eq 'y' -or $openReport -eq 'Y') {
            Start-Process $coverageFile
        }
    }
}

# Final summary
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Blue
if ($success) {
    Write-Host "✅ All tests completed successfully!" -ForegroundColor Green
    Write-Host "🎉 SmartQuest test suite is healthy!" -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed!" -ForegroundColor Red
    Write-Host "🔧 Please check the output above for details." -ForegroundColor Yellow
}
Write-Host "=" * 60 -ForegroundColor Blue

# Exit with appropriate code
exit $(if ($success) { 0 } else { 1 })
