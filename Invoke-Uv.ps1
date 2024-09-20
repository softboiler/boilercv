<#.SYNOPSIS
Invoke `uv`.#>
[CmdletBinding(PositionalBinding = $false)]
Param(
    [switch]$Sync,
    [switch]$Update,
    [switch]$Low,
    [switch]$High,
    [switch]$Build,
    [switch]$Force,
    [string]$PythonVersion = (Get-Content '.python-version'),
    [string]$PylanceVersion = (Get-Content '.pylance-version'),
    [switch]$CI = $Env:SYNC_ENV_DISABLE_CI ? $null : $Env:CI,
    [switch]$Devcontainer =
    $Env:SYNC_ENV_DISABLE_DEVCONTAINER ? $null : $Env:DEVCONTAINER,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Run
)

./Dev.ps1

$InvokeUvArgs = @{
    Sync           = $Sync
    Update         = $Update
    Low            = $Low
    High           = $High
    Build          = $Build
    Force          = $Force
    PythonVersion  = $PythonVersion
    PylanceVersion = $PylanceVersion
    CI             = $CI
    Devcontainer   = $Devcontainer
    Run            = $Run
}
Invoke-Uv @InvokeUvArgs
