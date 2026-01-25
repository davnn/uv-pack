[CmdletBinding()]
param(
  [string]$VenvDir = $env:VENV_DIR,
  [string]$BasePy  = $env:BASE_PY,
  [string]$PyDest  = $env:PY_DEST
)

$ErrorActionPreference = "Stop"

$PackDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $VenvDir) { $VenvDir = Join-Path $PackDir ".venv" }
if (-not $PyDest) { $PyDest = Join-Path $PackDir ".python" }

$ReqFile   = Join-Path $PackDir "requirements.txt"
$WheelsDir = Join-Path $PackDir "wheels"
$VendorDir = Join-Path $PackDir "vendor"
$PySrc     = Join-Path $PackDir "python"

function Find-Python($Root) {
  Get-ChildItem -Path $Root -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq "python.exe" } |
    Select-Object -ExpandProperty FullName |
    Sort-Object |
    Select-Object -First 1
}

function Find-Archive {
  if (-not (Test-Path $PySrc)) { return $null }
  Get-ChildItem -Path $PySrc -Filter *.tar.gz -File |
    Sort-Object Name |
    Select-Object -First 1 |
    Select-Object -ExpandProperty FullName
}

$Archive = Find-Archive
$HasArchive = [bool]$Archive

if ($HasArchive) {
  New-Item -ItemType Directory -Force -Path $PyDest | Out-Null
  $found = Find-Python $PyDest

  if (-not $found) {
    tar -C $PyDest -xzf $Archive
    Write-Host "Extracted python to $PyDest"
    $found = Find-Python $PyDest
  }

  if ($found) { $BasePy = $found }
}

if (-not $BasePy) {
  if (-not $HasArchive) {
    throw "BASE_PY must be set when no python archive is provided"
  }
  throw "Bundled python not found after extracting archive"
}

if (-not (Test-Path $BasePy)) {
  throw "BASE_PY not found: $BasePy"
}

Write-Host "Using base interpreter: $BasePy"
& $BasePy -m venv $VenvDir

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
  throw "Venv python missing"
}

$env:PIP_NO_INDEX = "1"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

try {
  & $VenvPython -m ensurepip --upgrade --default-pip | Out-Null
} catch { }

& $VenvPython -m pip install `
  --find-links $WheelsDir `
  --find-links $VendorDir `
  -r $ReqFile

Write-Host "Done."
Write-Host "Activate with:"
Write-Host "  $(Join-Path $VenvDir 'Scripts\Activate.ps1')"
