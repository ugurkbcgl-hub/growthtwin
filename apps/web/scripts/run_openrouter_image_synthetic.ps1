#Requires -Version 7.0

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("--estimate", "--run")]
    [string] $Mode
)

$ErrorActionPreference = "Stop"
$webRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $webRoot ".venv\Scripts\python.exe"
$openRouterSecretPath = Join-Path $env:LOCALAPPDATA "GrowthTwin\secrets\openrouter-api-key.dpapi"

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "The local Python environment is missing."
}

if ($Mode -eq "--estimate") {
    Push-Location $webRoot
    try {
        & $pythonPath scripts/evaluate_openrouter_image_synthetic.py --estimate
        exit $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path -LiteralPath $openRouterSecretPath -PathType Leaf)) {
    throw "The protected OpenRouter credential is missing."
}

$encryptedValue = [System.IO.File]::ReadAllText($openRouterSecretPath).Trim()
$secureValue = ConvertTo-SecureString -String $encryptedValue
$valuePointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
try {
    $apiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($valuePointer)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($valuePointer)
    $secureValue.Dispose()
    $encryptedValue = $null
}

$previousKey = [Environment]::GetEnvironmentVariable("OPENROUTER_API_KEY", "Process")
$previousLimitAssertion = [Environment]::GetEnvironmentVariable(
    "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED", "Process"
)
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", $apiKey, "Process")
[Environment]::SetEnvironmentVariable(
    "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED", "1", "Process"
)

$pythonExitCode = 1
Push-Location $webRoot
try {
    & $pythonPath scripts/evaluate_openrouter_image_synthetic.py --run
    $pythonExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
    [Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", $previousKey, "Process")
    [Environment]::SetEnvironmentVariable(
        "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED",
        $previousLimitAssertion,
        "Process"
    )
    $apiKey = $null
}

exit $pythonExitCode
