# ===============================
# Setup Python 3.13 + Venv + Install requirements
# ===============================

Write-Host "Checking for Python 3.13..."

$pythonVersion = python --version 2>$null

if ($pythonVersion -like "*3.13*") {
    Write-Host "Python 3.13 already installed"
}
else {
    Write-Host "Python 3.13 not found. Removing old Python versions..."

    # Remove all python installs safely
    Get-ChildItem "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall" , "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall" |
      Get-ItemProperty |
      Where-Object { $_.DisplayName -like "Python*" } |
      ForEach-Object {
          Write-Host "Uninstalling:" $_.DisplayName
          Start-Process -FilePath $_.UninstallString -ArgumentList "/quiet" -Wait
      }

    Write-Host "⬇ Downloading Python 3.13 installer..."
    Invoke-WebRequest "https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe" -OutFile "python_installer.exe"

    Write-Host "Installing Python..."    
    Start-Process "python_installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
}

# Refresh environment
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine")

Write-Host "Python Installed version:" (python --version)

Write-Host "Checking venv..."
if (!(Test-Path "./venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
} else {
    Write-Host "venv already exists"
}

Write-Host "Activating venv..."
& "./venv/Scripts/Activate.ps1"

Write-Host "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Opening VS Code..."
code .
