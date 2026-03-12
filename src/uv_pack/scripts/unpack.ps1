[CmdletBinding()]
param(
  [AllowEmptyString()][string]$VenvDir = $env:VENV_DIR,
  [string]$BasePy  = $env:BASE_PY,
  [string]$PyDest  = $env:PYTHON_DIR
)

$ErrorActionPreference = "Stop"

$PackDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HasVenvDir = $PSBoundParameters.ContainsKey("VenvDir") -or $null -ne $env:VENV_DIR
if (-not $HasVenvDir) { $VenvDir = Join-Path $PackDir ".venv" }
if (-not $PyDest) { $PyDest = Join-Path $PackDir ".python" }

$ReqFile   = Join-Path $PackDir "requirements.txt"
$WheelsDir = Join-Path $PackDir "wheels"
$VendorDir = Join-Path $PackDir "vendor"
$PySrc     = Join-Path $PackDir "python"

function Find-Python([string]$Root) {
  Get-ChildItem -Path $Root -Recurse -File -Filter python.exe -ErrorAction SilentlyContinue |
    Sort-Object { $_.FullName.Length } |
    Select-Object -First 1 -ExpandProperty FullName
}

$Archive = if (Test-Path $PySrc) {
  Get-ChildItem -Path $PySrc -File -Filter *.tar.gz | Sort-Object Name | Select-Object -First 1 -ExpandProperty FullName
}

if (-not $BasePy -and ((Test-Path $PyDest) -or $Archive)) {
  New-Item -ItemType Directory -Force -Path $PyDest | Out-Null
  $BasePy = Find-Python $PyDest
  if (-not $BasePy -and $Archive) {
    tar -C $PyDest -xzf $Archive
    Write-Host "Extracted python to $PyDest"
    $BasePy = Find-Python $PyDest
  }
}

if (-not $BasePy) {
  throw $(
    if ($Archive) { "Bundled python not found after extracting archive" }
    else { "BASE_PY must be set when no python archive is provided" }
  )
}
if (-not (Test-Path $BasePy)) { throw "BASE_PY not found: $BasePy" }

Write-Host "Using base interpreter: $BasePy"
$VenvPython = $BasePy
if ($VenvDir) {
  & $BasePy -m venv $VenvDir
  $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
  if (-not (Test-Path $VenvPython)) { throw "Venv python missing" }
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
if ($VenvDir) { Write-Host "Activate with:"; Write-Host "  $(Join-Path $VenvDir 'Scripts\Activate.ps1')" }
