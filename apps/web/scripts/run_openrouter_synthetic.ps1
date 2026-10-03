#Requires -Version 7.0

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $RunnerArguments
)

$ErrorActionPreference = "Stop"
$webRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $webRoot ".venv\Scripts\python.exe"
$manageSecretPath = Join-Path $env:LOCALAPPDATA "GrowthTwin\secrets\django-secret-key.dpapi"
$openRouterSecretPath = Join-Path $env:LOCALAPPDATA "GrowthTwin\secrets\openrouter-api-key.dpapi"

function Read-LocalProtectedSecret {
    param([Parameter(Mandatory = $true)][string] $Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required protected local credential is missing: $Path"
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

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "The local Python environment is missing."
}

if ($RunnerArguments -contains "--estimate") {
    $previousDjangoSecret = [Environment]::GetEnvironmentVariable("DJANGO_SECRET_KEY", "Process")
    [Environment]::SetEnvironmentVariable(
        "DJANGO_SECRET_KEY",
        (Read-LocalProtectedSecret -Path $manageSecretPath),
        "Process"
    )
    Push-Location $webRoot
    try {
        & $pythonPath scripts/evaluate_openrouter_synthetic.py @RunnerArguments
        $pythonExitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
        [Environment]::SetEnvironmentVariable("DJANGO_SECRET_KEY", $previousDjangoSecret, "Process")
    }
    exit $pythonExitCode
}

$confirmation = Read-Host "Confirm: this dedicated key has a USD 16 limit with no reset, the account has sufficient existing credits, and auto-recharge is off. Type RUN to continue"
if ($confirmation -cne "RUN") {
    Write-Output "Evaluation cancelled before any provider request."
    exit 2
}

$processSettings = [ordered]@{
    DJANGO_SECRET_KEY = Read-LocalProtectedSecret -Path $manageSecretPath
    OPENROUTER_API_KEY = Read-LocalProtectedSecret -Path $openRouterSecretPath
    GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED = "1"
}
$previousSettings = @{}
$settingNames = @($processSettings.Keys)
foreach ($settingName in $settingNames) {
    $previousSettings[$settingName] = [Environment]::GetEnvironmentVariable($settingName, "Process")
    [Environment]::SetEnvironmentVariable($settingName, $processSettings[$settingName], "Process")
}

$pythonExitCode = 1
Push-Location $webRoot
try {
    & $pythonPath scripts/evaluate_openrouter_synthetic.py @RunnerArguments
    $pythonExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
    foreach ($settingName in $settingNames) {
        [Environment]::SetEnvironmentVariable($settingName, $previousSettings[$settingName], "Process")
    }
    foreach ($settingName in $settingNames) {
        $processSettings[$settingName] = $null
    }
}

exit $pythonExitCode
