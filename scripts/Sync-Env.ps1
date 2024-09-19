<#.SYNOPSIS
Initialize shell environment.#>

Param(
    # Python version.
    [string]$Version,
    # Sync to highest dependencies.
    [switch]$High,
    # Perform minimal sync for release workflow.
    [switch]$Release,
    # Just check the lock is valid when syncing.
    [switch]$Locked
)

. scripts/Common.ps1

# ? Error-handling
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$ErrorView = 'NormalView'

# ? Fix leaky UTF-8 encoding settings on Windows
if ($IsWindows) {
    # ? Now PowerShell pipes will be UTF-8. Note that fixing it from Control Panel and
    # ? system-wide has buggy downsides.
    # ? See: https://github.com/PowerShell/PowerShell/issues/7233#issuecomment-640243647
    [console]::InputEncoding = [console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
}

$Version = $Version ? $Version : (Get-Content '.copier-answers.yml' |
        Find-Pattern '^python_version:\s?["'']([^"'']+)["'']$' |
        Find-Pattern '^([^.]+\.[^.]+).*$')
$High = $High ? $High : [bool]$Env:SYNC_PY_HIGH
$CI = $Env:SYNC_PY_DISABLE_CI ? $null : $Env:CI
$Devcontainer = $Env:SYNC_PY_DISABLE_DEVCONTAINER ? $null : $Env:DEVCONTAINER

if (!$CI) {
    Sync-Uv -Version '0.4.10'
    Get-ChildItem '.git/modules' -Filter 'config.lock' -Recurse -Depth 1 | Remove-Item
    git submodule update --init --merge
}

if ($Locked) {
    if ($High) { Sync-DevEnv -Locked -High } else { Sync-DevEnv -Locked }
}
else {
    if ($High) { Sync-DevEnv -High } else { Sync-DevEnv }
}
if ($Release) { return }

if ($Devcontainer) {
    $Repo = Get-ChildItem '/workspaces'
    $Packages = Get-ChildItem "$Repo/packages"
    $SafeDirs = @($Repo) + $Packages
    foreach ($Dir in $SafeDirs) {
        if (!($SafeDirs -contains $Dir)) {
            git config --global --add safe.directory $Dir
        }
    }
}

if ($CI) { dev elevate-pyright-warnings }
else {
    $Hooks = '.git/hooks'
    if (!(Test-Path "$Hooks/post-checkout") -or !(Test-Path "$Hooks/pre-commit") -or
        !(Test-Path "$Hooks/pre-push")
    ) { pre-commit install }
    if (!$Devcontainer -and (Get-Command -Name 'code' -ErrorAction 'Ignore') -and
        $Env:PYRIGHT_PYTHON_PYLANCE_VERSION
    ) {
        $LocalExtensions = '.vscode/extensions'
        $Pylance = 'ms-python.vscode-pylance'
        if (!(Test-Path "$LocalExtensions/$Pylance-$Env:PYRIGHT_PYTHON_PYLANCE_VERSION")) {
            $Install = @(
                "--extensions-dir=$LocalExtensions",
                "--install-extension=$Pylance@$Env:PYRIGHT_PYTHON_PYLANCE_VERSION"
            )
            code @Install
            if (!(Test-Path $LocalExtensions)) {
                'COULD NOT INSTALL PYLANCE LOCALLY' | Write-Progress -Info
                'PROCEEDING WITHOUT LOCAL PYLANCE INSTALL' | Write-Progress -Done
            }
            else {
                $PylanceExtension = Get-ChildItem -Path $LocalExtensions -Filter "$Pylance-*"
                # ? Remove other files
                Get-ChildItem -Path $LocalExtensions |
                    Where-Object { Compare-Object $_ $PylanceExtension } |
                    Remove-Item -Recurse
                # ? Remove local Pylance bundled stubs
                $PylanceExtension |
                    ForEach-Object { Get-ChildItem "$_/dist/bundled" -Filter '*stubs' } |
                    Remove-Item -Recurse
                'INSTALLED PYLANCE LOCALLY' | Write-Progress -Done
            }
        }
    }
}
