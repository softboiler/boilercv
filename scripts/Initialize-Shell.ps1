<#
.SYNOPSIS
Initialization commands for PowerShell shells in pre-commit and tasks.#>

# ? Error-handling
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$ErrorView = 'NormalView'

# ? Fix leaky UTF-8 encoding settings on Windows
if ($IsWindows) {
    # Now PowerShell pipes will be UTF-8. Note that fixing it from Control Panel and
    # system-wide has buggy downsides.
    # See: https://github.com/PowerShell/PowerShell/issues/7233#issuecomment-640243647
    [console]::InputEncoding = [console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
}

# ? Environment setup
function Set-Env {
    <#.SYNOPSIS
    Activate virtual environment and set environment variables.#>
    # ? Activate virtual environment if one exists
    if (Test-Path '.venv') {
        if ($IsWindows) { .venv/scripts/activate.ps1 } else { .venv/bin/activate.ps1 }
    }
    # ? Set environment variables
    $Vars = $Env:GITHUB_ENV ? $(Get-Content $Env:GITHUB_ENV |
            Select-String -Pattern '^(.+)=.+$' |
            ForEach-Object { $_.Matches.Groups[1].value }) : @{}
    if ((Test-Path '.venv') -or ($Env:GITHUB_ENV)) {
        foreach ($line in boilercv_tools init-shell) {
            $Key, $Value = $line -Split '=', 2
            Set-Item "Env:$Key" $Value
            if ($Env:GITHUB_ENV -and ($Key -notin $Vars)) {
                "$Key=$Value" >> $Env:GITHUB_ENV
            }
        }
    }
}
Set-Env
