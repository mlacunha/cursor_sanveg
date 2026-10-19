# Create a deploy package similar to the `temp` folder contents
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

$deployDir = Join-Path $root "..\deploy"
if (Test-Path $deployDir) { Remove-Item $deployDir -Recurse -Force }
New-Item -ItemType Directory -Path $deployDir | Out-Null

# List of files/dirs to include (relative to repo root)
$include = @(
    'main.py',
    'Procfile',
    'gunicorn.conf.py',
    'passenger_wsgi.py',
    'start.sh',
    'requirements.txt',
    'runtime.txt',
    'USAGE.md',
    'README_DEPLOY.md',
    'app',
    'scripts',
    'app/config',
    'app/routers',
    'app/models',
    'app/schemas',
    'app/utils'
)

# Copy files and directories
foreach ($item in $include) {
    $src = Join-Path $root "..\$item"
    if (Test-Path $src) {
        $dest = Join-Path $deployDir $item
        $parent = Split-Path -Parent $dest
        if (!(Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }

        if (Test-Path $src -PathType Container) {
            Write-Host "Copying directory: $item"
            Copy-Item -Path $src -Destination $dest -Recurse -Force
        } else {
            Write-Host "Copying file: $item"
            Copy-Item -Path $src -Destination $dest -Force
        }
    } else {
        Write-Host "Warning: $item not found, skipping"
    }
}

# Remove virtualenv, .git, __pycache__ and other unwanted files from deploy
Get-ChildItem -Path $deployDir -Recurse -Force | Where-Object { $_.Name -in @('.git', 'venv', '__pycache__') } | ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }

# Create zip
$zipPath = Join-Path $root "..\svegpa-api-deploy-updated.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($deployDir, $zipPath)

Write-Host "Deploy package created at: $zipPath"
