#Requires -Version 7.0

param(
    [Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)]
    [string[]] $DjangoArguments
)

$ErrorActionPreference = "Stop"

$secretDirectory = Join-Path $env:LOCALAPPDATA "GrowthTwin\secrets"
$applicationPasswordFile = Join-Path $secretDirectory "postgres-app-password.dpapi"
$djangoSecretFile = Join-Path $secretDirectory "django-secret-key.dpapi"

function Read-LocalProtectedSecret {
    param([Parameter(Mandatory = $true)][string] $Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Local credentials are not set up. Run scripts\setup-local-postgres.ps1 first."
    }

    $encryptedValue = [System.IO.File]::ReadAllText($Path).Trim()
    $secureValue = ConvertTo-SecureString -String $encryptedValue
    $valuePointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($valuePointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($valuePointer)
        $secureValue.Dispose()
    }
}

$webRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $webRoot ".venv\Scripts\python.exe"
$managePath = Join-Path $webRoot "manage.py"

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "The local Python environment is missing. Install the apps/web dependencies first."
}

$processSettings = [ordered]@{
    DJANGO_SECRET_KEY = Read-LocalProtectedSecret -Path $djangoSecretFile
    POSTGRES_DB = "growthtwin"
    POSTGRES_USER = "growthtwin_app"
    POSTGRES_PASSWORD = Read-LocalProtectedSecret -Path $applicationPasswordFile
    POSTGRES_HOST = "127.0.0.1"
    POSTGRES_PORT = "5432"
}

$previousSettings = @{}
$settingNames = @($processSettings.Keys)
foreach ($settingName in $settingNames) {
    $previousSettings[$settingName] = [Environment]::GetEnvironmentVariable($settingName, "Process")
    [Environment]::SetEnvironmentVariable($settingName, $processSettings[$settingName], "Process")
}

$pythonExitCode = 1
try {
    & $pythonPath $managePath @DjangoArguments
    $pythonExitCode = $LASTEXITCODE
}
finally {
    foreach ($settingName in $settingNames) {
        [Environment]::SetEnvironmentVariable($settingName, $previousSettings[$settingName], "Process")
    }
    foreach ($settingName in $settingNames) {
        $processSettings[$settingName] = $null
    }
}

exit $pythonExitCode
