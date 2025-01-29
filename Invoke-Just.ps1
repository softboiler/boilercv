<#.SYNOPSIS
Invoke `just`.#>
[CmdletBinding(PositionalBinding = $False)]
Param(
    [switch]$Sync,
    [switch]$Update,
    [switch]$Low,
    [switch]$High,
    [switch]$Build,
    [switch]$Force,
    [switch]$_CI,
    [switch]$Locked,
    [switch]$Devcontainer,
    [string]$PythonVersion = (Get-Content '.python-version'),
    [string]$PylanceVersion = (Get-Content '.pylance-version'),
    [Parameter(ValueFromPipeline, ValueFromRemainingArguments)][string[]]$Run
)
Begin {
    . ./dev.ps1

    $_CI = (New-Switch $Env:SYNC_ENV_DISABLE_CI (New-Switch $Env:CI))
    $InvokeUvArgs = @{
        Sync           = $Sync
        Update         = $Update
        Low            = $Low
        High           = $High
        Build          = $Build
        Force          = $Force
        _CI            = $_CI
        Locked         = $_CI
        Devcontainer   = (New-Switch $Env:SYNC_ENV_DISABLE_DEVCONTAINER (New-Switch $Env:DEVCONTAINER))
        PythonVersion  = $PythonVersion
        PylanceVersion = $PylanceVersion
    }
}
Process { Invoke-Just @InvokeUvArgs @Run }
