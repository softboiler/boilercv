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
    return
    # ? Set environment variables
    $EnvFile = $Env:GITHUB_ENV ? $Env:GITHUB_ENV : '.env'
    if (!(Test-Path $EnvFile)) { New-Item $EnvFile }
    $Vars = $(Get-Content $EnvFile |
            Select-String -Pattern '^(.+)=.+$' |
            ForEach-Object { $_.Matches.Groups[1].value })
    if (Get-Command -Name 'boilercv_tools' -ErrorAction 'Ignore') {
        foreach ($line in boilercv_tools init-shell) {
            $Key, $Value = $line -Split '=', 2
            Set-Item "Env:$Key" $Value
            if (($Key -ne 'PATH') -and ($Key -notin $Vars)) {
                "$Key=$Value" >> $EnvFile
            }
        }
    }
}
Set-Env
