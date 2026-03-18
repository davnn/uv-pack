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

function Find-Python($Root) {
  Get-ChildItem -Path $Root -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq "python.exe" } |
    Select-Object -ExpandProperty FullName |
    Sort-Object { $_.Length } |
    Select-Object -First 1
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
  Write-Host "No bundled python or BASE_PY provided. Searching for system python..."
  foreach ($cmd in "python", "python3") {
    $SysPy = Get-Command $cmd -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
    if ($SysPy) {
      Write-Host "Found system python: $SysPy"
      $Confirm = Read-Host "Do you want to use this python for installation? [Y/n]"
      if ($Confirm -notmatch "^[nN](o)?$") {
        $BasePy = $SysPy
        break
      }
    }
  }
}

if (-not $BasePy) {
  throw "BASE_PY must be set when no python archive is provided and no system python is accepted."
}
if (-not (Test-Path $BasePy)) { throw "BASE_PY not found: $BasePy" }

Write-Host "Using base interpreter: $BasePy"
$VenvPython = $BasePy
$HasUv = Get-Command uv -ErrorAction SilentlyContinue

if (-not $HasUv) {
  $UvWheel = Get-ChildItem -Path $WheelsDir -File -Filter "uv-*.whl" | Select-Object -First 1 -ExpandProperty FullName
  if ($UvWheel) {
    Write-Host "uv not found, installing from $UvWheel..."
    & $BasePy -m pip install $UvWheel | Out-Null
    $HasUv = Get-Command uv -ErrorAction SilentlyContinue
  }
}

if ($VenvDir) {
  if (Test-Path $VenvDir) {
    Write-Host "Virtual environment already exists at $VenvDir, skipping creation."
  } else {
    if ($HasUv) {
      & uv venv $VenvDir --python $BasePy --quiet
    } else {
      & $BasePy -m venv $VenvDir
    }
  }
  $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
  if (-not (Test-Path $VenvPython)) { throw "Venv python missing" }
}

if ($HasUv) {
  & uv pip install --python $VenvPython --no-index --find-links $WheelsDir --find-links $VendorDir -r $ReqFile --quiet
} else {
  $env:PIP_NO_INDEX = "1"
  $env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

  try {
    & $VenvPython -m ensurepip --upgrade --default-pip | Out-Null
  } catch { }

  & $VenvPython -m pip install `
    --find-links $WheelsDir `
    --find-links $VendorDir `
    -r $ReqFile
}

Write-Host "Done."
if ($VenvDir) { Write-Host "Activate with:"; Write-Host "  $(Join-Path $VenvDir 'Scripts\Activate.ps1')" }
