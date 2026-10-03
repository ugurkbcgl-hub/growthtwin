#Requires -Version 7.0

$ErrorActionPreference = "Stop"
$secretDirectory = Join-Path $env:LOCALAPPDATA "GrowthTwin\secrets"
$secretPath = Join-Path $secretDirectory "openrouter-api-key.dpapi"

New-Item -ItemType Directory -Path $secretDirectory -Force | Out-Null
$secureValue = Read-Host "OpenRouter API key (hidden; stored for this Windows account only)" -AsSecureString
try {
    if ($secureValue.Length -lt 1 -or $secureValue.Length -gt 512) {
        throw "The API key length is invalid. No key was stored."
    }

    $encryptedValue = ConvertFrom-SecureString -SecureString $secureValue
    [System.IO.File]::WriteAllText($secretPath, $encryptedValue)
    Write-Output "OpenRouter key stored in the current Windows user's protected local secret folder."
}
finally {
    $secureValue.Dispose()
}
