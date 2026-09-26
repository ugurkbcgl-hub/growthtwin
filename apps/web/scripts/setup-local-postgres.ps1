#Requires -Version 7.0

$ErrorActionPreference = "Stop"

$databaseName = "growthtwin"
$applicationRole = "growthtwin_app"
$postgresBin = "C:\Program Files\PostgreSQL\18\bin"
$psqlPath = Join-Path $postgresBin "psql.exe"
$secretDirectory = Join-Path $env:LOCALAPPDATA "GrowthTwin\secrets"
$applicationPasswordFile = Join-Path $secretDirectory "postgres-app-password.dpapi"
$djangoSecretFile = Join-Path $secretDirectory "django-secret-key.dpapi"

function Invoke-PsqlWithPasswordInput {
    param(
        [Parameter(Mandatory = $true)][string[]] $Arguments,
        [Parameter(Mandatory = $true)][string[]] $PasswordLines
    )

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $psqlPath
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    # PostgreSQL on Windows may otherwise read hidden prompts directly from CONIN$.
    $startInfo.Environment['OSTYPE'] = 'msys'
    foreach ($argument in $Arguments) {
        $startInfo.ArgumentList.Add($argument)
    }

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    try {
        if (-not $process.Start()) {
            throw "Could not start the local PostgreSQL client."
        }
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()
        foreach ($passwordLine in $PasswordLines) {
            $process.StandardInput.WriteLine($passwordLine)
        }
        $process.StandardInput.Close()
        $process.WaitForExit()
        $stdoutTask.GetAwaiter().GetResult() | Out-Null
        $stderrTask.GetAwaiter().GetResult() | Out-Null
        return $process.ExitCode
    }
    finally {
        $process.Dispose()
    }
}

if (-not (Test-Path -LiteralPath $psqlPath -PathType Leaf)) {
    throw "PostgreSQL command-line tools were not found at the expected install path."
}

$adminSecureString = Read-Host "Enter the postgres administrator password chosen during installation (input is hidden)" -AsSecureString
$adminPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($adminSecureString)
$adminPassword = $null
$applicationPassword = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$djangoSecretKey = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(48)).TrimEnd("=").Replace("+", "-").Replace("/", "_")
$adminPassFile = Join-Path $env:TEMP ("growthtwin-postgres-setup-" + [guid]::NewGuid().ToString("N") + ".sql")
$applicationPasswordSecure = $null
$djangoSecretSecure = $null

try {
    $adminPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($adminPointer)

    $setupSql = @'
\set ON_ERROR_STOP on
DO $block$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'growthtwin_app') THEN
        CREATE ROLE growthtwin_app LOGIN;
    END IF;
END;
$block$;
ALTER ROLE growthtwin_app WITH LOGIN;
SELECT 'CREATE DATABASE growthtwin OWNER growthtwin_app'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'growthtwin')
\gexec
ALTER DATABASE growthtwin OWNER TO growthtwin_app;
\password growthtwin_app
\q
'@
    [System.IO.File]::WriteAllText($adminPassFile, $setupSql, [System.Text.UTF8Encoding]::new($false))

    Write-Output "Setting up the local database. The generated application password will stay hidden and be protected for this Windows user."
    $setupExitCode = Invoke-PsqlWithPasswordInput -Arguments @(
        '--no-psqlrc', '--quiet', '--set', 'ON_ERROR_STOP=1', '--host=127.0.0.1', '--port=5432',
        '--username=postgres', '--dbname=postgres', '--password', '--file', $adminPassFile
    ) -PasswordLines @($adminPassword, $applicationPassword, $applicationPassword)
    if ($setupExitCode -ne 0) {
        throw "Local database setup failed. Check the postgres password and rerun setup. No new credentials were saved."
    }

    Remove-Item -LiteralPath $applicationPasswordFile, $djangoSecretFile -Force -ErrorAction SilentlyContinue
    $verificationSql = @"
DO `$verify`$
BEGIN
    IF current_database() <> '$databaseName'
       OR current_user <> '$applicationRole'
       OR NOT EXISTS (
           SELECT 1
           FROM pg_database
           WHERE datname = current_database()
             AND datdba = (SELECT oid FROM pg_roles WHERE rolname = current_user)
       ) THEN
        RAISE EXCEPTION 'GrowthTwin local database/role verification failed';
    END IF;
END;
`$verify`$;
"@
    Write-Output "Verifying the local application role and database."
    $verificationExitCode = Invoke-PsqlWithPasswordInput -Arguments @(
        '--no-psqlrc', '--quiet', '--set', 'ON_ERROR_STOP=1', '--host=127.0.0.1', '--port=5432',
        "--username=$applicationRole", "--dbname=$databaseName", '--password', '--command', $verificationSql
    ) -PasswordLines @($applicationPassword)
    if ($verificationExitCode -ne 0) {
        throw "The generated application credentials failed the database verification. Rerun setup; no new credentials were saved."
    }

    $applicationPasswordSecure = ConvertTo-SecureString -String $applicationPassword -AsPlainText -Force
    $djangoSecretSecure = ConvertTo-SecureString -String $djangoSecretKey -AsPlainText -Force
    $applicationPasswordEncrypted = ConvertFrom-SecureString -SecureString $applicationPasswordSecure
    $djangoSecretEncrypted = ConvertFrom-SecureString -SecureString $djangoSecretSecure
    [System.IO.Directory]::CreateDirectory($secretDirectory) | Out-Null
    [System.IO.File]::WriteAllText($applicationPasswordFile, $applicationPasswordEncrypted, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($djangoSecretFile, $djangoSecretEncrypted, [System.Text.UTF8Encoding]::new($false))

    Write-Output "Created and verified the local GrowthTwin database and restricted application role."
    Write-Output "Generated credentials are protected outside the repository for this Windows user."
}
finally {
    Remove-Item -LiteralPath $adminPassFile -Force -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($adminPointer)
    $adminPassword = $null
    $applicationPassword = $null
    $djangoSecretKey = $null
    $applicationPasswordEncrypted = $null
    $djangoSecretEncrypted = $null
    $adminSecureString.Dispose()
    if ($null -ne $applicationPasswordSecure) {
        $applicationPasswordSecure.Dispose()
    }
    if ($null -ne $djangoSecretSecure) {
        $djangoSecretSecure.Dispose()
    }
}
