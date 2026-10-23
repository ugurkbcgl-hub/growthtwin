# Source this helper; it reads no credentials and starts no processes.
function Get-YaparoPython {
    param([Parameter(Mandatory = $true)][string] $WebRoot)

    $privatePython = Join-Path $env:USERPROFILE '.yaparo\.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $privatePython -PathType Leaf) {
        return $privatePython
    }
    $separator = [IO.Path]::DirectorySeparatorChar
    $fullWebRoot = [IO.Path]::GetFullPath($WebRoot).TrimEnd($separator)
    $syncRoots = @($env:OneDrive, $env:OneDriveCommercial, (Join-Path $env:USERPROFILE 'OneDrive'))
    foreach ($syncRoot in $syncRoots) {
        if ($syncRoot) {
            $normalizedRoot = [IO.Path]::GetFullPath($syncRoot).TrimEnd($separator)
            if ($fullWebRoot.Equals($normalizedRoot, [StringComparison]::OrdinalIgnoreCase) -or
                $fullWebRoot.StartsWith(($normalizedRoot + $separator), [StringComparison]::OrdinalIgnoreCase)) {
                throw 'Create the private Yaparo Python environment outside OneDrive; see apps/web/README.md.'
            }
        }
    }
    $candidates = @(
        (Join-Path $WebRoot '.venv\Scripts\python.exe'),
        (Join-Path (Split-Path -Parent (Split-Path -Parent $WebRoot)) '.venv\Scripts\python.exe')
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }
    throw 'Yaparo Python environment is missing. See apps/web/README.md.'
}
