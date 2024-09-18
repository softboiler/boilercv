<#.SYNOPSIS
Initialize shell environment.#>

Param(
    # Python version.
    [string]$Version,
    # Sync to highest dependencies.
    [switch]$High,
    # Perform minimal sync for release workflow.
    [switch]$Release
)

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

function Find-Pattern {
    <#.SYNOPSIS
    Find the first match to a pattern in a string.#>
    Param(
        [Parameter(Mandatory)][string]$Pattern,
        [Parameter(Mandatory, ValueFromPipeline)][string]$String
    )
    process {
        if ($Groups = ($String | Select-String -Pattern $Pattern).Matches.Groups) {
            return $Groups[1].value
        }
    }
}

$Version = $Version ? $Version : (Get-Content '.copier-answers.yml' |
        Find-Pattern '^python_version:\s?["'']([^"'']+)["'']$' |
        Find-Pattern '^([^.]+\.[^.]+).*$')
$High = $High ? $High : [bool]$Env:SYNC_PY_HIGH
$CI = $Env:SYNC_PY_DISABLE_CI ? $null : $Env:CI
$Devcontainer = $Env:SYNC_PY_DISABLE_DEVCONTAINER ? $null : $Env:DEVCONTAINER

function Write-Progress {
    <#.SYNOPSIS
    Write progress and completion messages.#>
    Param(
        [Parameter(Mandatory, ValueFromPipeline)][string]$Message,
        [switch]$Done,
        [switch]$Info
    )
    begin {
        $InProgress = !$Done -and !$Info
        if ($Info) { $Color = 'Magenta' }
        elseif ($Done) { $Color = 'Green' }
        else { $Color = 'Yellow' }
    }
    process {
        if ($InProgress) { Write-Host }
        "$Message$($InProgress ? '...' : '')" | Write-Host -ForegroundColor $Color
    }
}

function Set-Env {
    <#.SYNOPSIS
    Activate virtual environment and set environment variables.#>

    # ? Track environment variables to update `.env` with later
    $EnvVars = @{}
    $Sep = $IsWindows ? ';' : ':'
    $EnvPath = $Env:GITHUB_ENV ? $Env:GITHUB_ENV : '.env'
    # ? Create `env` if missing
    if (!($EnvFile = Get-Item $EnvPath -ErrorAction 'Ignore')) {
        New-Item $EnvPath
        $EnvFile = Get-Item $EnvPath
    }
    # ? Create local `bin` if missing
    if (!($Bin = Get-Item 'bin' -ErrorAction 'Ignore')) {
        New-Item 'bin' -ItemType 'Directory'
        $Bin = Get-Item 'bin'
    }
    # ? Add local `bin` to path
    $Path = $Env:PATH = "$Bin$Sep$Env:PATH"
    # ? Set `uv` tool directory to local `bin`
    $UvToolBinDirKey = 'UV_TOOL_BIN_DIR'
    Set-Item "Env:$UvToolBinDirKey" $Bin
    $EnvVars.Add($UvToolBinDirKey, $Bin)


    function Sync-Uv {
        <#.SYNOPSIS
        Sync local `uv` version.#>
        Param([string]$Version)
        if (Get-Command 'uv' -ErrorAction 'Ignore') { $Uv = 'uv' }
        else {
            $Uv = Get-Item 'bin/uv.*' -ErrorAction 'Ignore'
        }
        if ((!$Uv -or !(& $Uv --version | Select-String $Version))) {
            'Installing uv' | Write-Progress
            $OrigCargoHome = $Env:CARGO_HOME
            $Env:CARGO_HOME = '.'
            $Env:INSTALLER_NO_MODIFY_PATH = $true
            if ($IsWindows) { Invoke-RestMethod "https://github.com/astral-sh/uv/releases/download/$Version/uv-installer.ps1" | Invoke-Expression }
            else { curl --proto '=https' --tlsv1.2 -LsSf "https://github.com/astral-sh/uv/releases/download/$Version/uv-installer.sh" | sh }
            if ($OrigCargoHome) { $Env:CARGO_HOME = $OrigCargoHome }
            'uv installed' | Write-Progress -Done
            return Get-Item 'bin/uv.*'
        }
    }
    '****** SYNCING' | Write-Progress
    Sync-Uv -Version '0.4.10'

    if ($CI) {
        'SYNCING PROJECT WITH TEMPLATE' | Write-Progress
        try { scripts/Sync-Template.ps1 -Stay } catch [System.Management.Automation.NativeCommandExitException] {
            git stash save --include-untracked
            scripts/Sync-Template.ps1 -Stay
            git stash pop
            git add .
        }
        'PROJECT SYNCED WITH TEMPLATE' | Write-Progress
    }

    # ? Sync contributor virtual environment
    $VenvPath = '.venv'
    if (!$CI) {
        if (!(Test-Path $VenvPath)) { uv venv --python $Version }

        # ? Set `uv` project environment to `.venv`
        $Venv = Get-Item $VenvPath
        $UvProjectEnvironment = 'UV_PROJECT_ENVIRONMENT'
        Set-Item "Env:$UvProjectEnvironment" $Venv
        $EnvVars.Add($UvProjectEnvironment, $Venv)

        # ? Activate the environment
        if ($IsWindows) { .venv/scripts/activate.ps1 } else { .venv/bin/activate.ps1 }

        # ? Recreate and reactivate it if it's the incorrect Python version
        if (!(python --version | Select-String -Pattern $([Regex]::Escape($Version)))) {
            'Virtual environment is the wrong Python version.' | Write-Progress -Info
            'Creating virtual environment with correct Python version' | Write-Progress
            Remove-Item -Recurse -Force $Env:VIRTUAL_ENV
            uv venv --python $Version
            if ($IsWindows) { .venv/scripts/activate.ps1 } else { .venv/bin/activate.ps1 }
        }
    }

    # ? Sync environment
    $RequirementsDir = Get-Item 'requirements'
    $RequirementsPath = $High ? "$RequirementsDir/requirements_high.txt" : "$RequirementsDir/requirements.txt"
    $DefaultLockPath = "$RequirementsDir/uv.lock"
    $LockPath = $High ? "$RequirementsDir/uv_high.lock" : 'uv.lock'
    if (!($Lock = Get-Item $LockPath -ErrorAction 'Ignore')) {
        New-Item $LockPath
        $Lock = Get-Item $LockPath
    }
    Push-Location $RequirementsDir
    $(if ($High) { uv export --resolution highest } else { uv export --resolution lowest-direct }) |
        ForEach-Object { $_ -Replace '^\.', '-e ' } |
        Set-Content $RequirementsPath
    Pop-Location
    Move-Item $DefaultLockPath $Lock -Force
    uv pip sync $Requirements (Get-Item $RequirementsPath)

    # ? Get environment variables from `pyproject.toml`
    boilercv_tools init-shell |
        Select-String -Pattern '^(.+)=(.+)$' |
        ForEach-Object {
            $Key, $Value = $_.Matches.Groups[1].Value, $_.Matches.Groups[2].Value
            if ((($Key.ToLower() -ne 'path')) -and ($EnvVars -notcontains $Key)) {
                $EnvVars.Add($Key, $Value)
            }
        }
    # ? Get environment variables to update in `.env`
    $Keys = @()
    $Lines = Get-Content $EnvFile | ForEach-Object {
        $_ -replace '^(?<Key>.+)=(?<Value>.+)$', {
            $Key = $_.Groups['Key'].Value
            if ($Key.ToLower() -eq 'path') { $PathInEnvFile = $true }
            elseif ($EnvVars.ContainsKey($Key)) {
                $Keys += $Key
                return "$Key=$($EnvVars[$Key])"
            }
            return $_
        }
    }
    # ? Sync environment variables and those in `.env`
    $NewLines = $EnvVars.GetEnumerator() | ForEach-Object {
        $Key, $Value = $_.Key, $_.Value
        if ($Key.ToLower() -ne 'path') {
            Set-Item "Env:$Key" $Value
            if ($Keys -notcontains $Key) { return "$Key=$Value" }
        }
    }
    @($Lines, $NewLines) | Set-Content $EnvFile
    if ($CI -and !$PathInEnvFile) { "PATH=$Path" | Add-Content $EnvFile }
}

Set-Env

'RUNNING POST-SYNC TASKS' | Write-Progress
'CHECKING ENVIRONMENT TYPE' | Write-Progress
if (!$Release -and $CI) { $msg = 'CI' }
elseif ($Devcontainer) { $msg = 'devcontainer' }
elseif ($Release) { $msg = 'release' }
else { $msg = 'local' }
if ($Release) {
    "Finished $msg steps" | Write-Progress -Info
    '****** DONE ******' | Write-Progress -Done
    return
}
"Will run $msg steps" | Write-Progress -Info
if ($CI) { boilercv_tools elevate-pyright-warnings }
if (!$CI -and !$Devcontainer -and
    (Get-Command -Name 'code' -ErrorAction 'Ignore') -and
    ($Env:PYRIGHT_PYTHON_PYLANCE_VERSION)
) {
    'INSTALLING PYLANCE LOCALLY' | Write-Progress
    $LocalExtensions = '.vscode/extensions'
    $Pylance = 'ms-python.vscode-pylance'
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
        # Remove other files
        Get-ChildItem -Path $LocalExtensions |
            Where-Object { Compare-Object $_ $PylanceExtension } |
            Remove-Item -Recurse
        # Remove local Pylance bundled stubs
        $PylanceExtension |
            ForEach-Object { Get-ChildItem "$_/dist/bundled" -Filter '*stubs' } |
            Remove-Item -Recurse
        'INSTALLED PYLANCE LOCALLY' | Write-Progress -Done
    }
}
if ($Devcontainer) {
    $repo = Get-ChildItem '/workspaces'
    $submodules = Get-ChildItem "$repo/submodules"
    $safeDirs = @($repo) + $submodules
    foreach ($dir in $safeDirs) {
        if (!($safeDirs -contains $dir)) { git config --global --add safe.directory $dir }
    }
}
if (!$CI) {
    'SYNCING SUBMODULES' | Write-Progress
    Get-ChildItem '.git/modules' -Filter 'config.lock' -Recurse -Depth 1 | Remove-Item
    git submodule update --init --merge
    'SUBMODULES SYNCED' | Write-Progress -Done
    '' | Write-Host
    'INSTALLING PRE-COMMIT HOOKS' | Write-Progress
    pre-commit install
    'PRE-COMMIT HOOKS INSTALLED' | Write-Progress -Done
    '' | Write-Host
}
'****** DONE ******' | Write-Progress -Done
