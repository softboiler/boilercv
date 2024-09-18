<#.SYNOPSIS
Common utilities.#>

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

function Sync-Uv {
    <#.SYNOPSIS
    Sync `uv` version.#>
    Param([string]$Version)
    if (
        !(Get-Command 'uv' -ErrorAction 'Ignore') -or
        !(uv --version | Select-String $Version)
    ) {
        $OrigCargoHome = $Env:CARGO_HOME
        $Env:CARGO_HOME = '.'
        $Env:INSTALLER_NO_MODIFY_PATH = $true
        if ($IsWindows) { Invoke-RestMethod "https://github.com/astral-sh/uv/releases/download/$Version/uv-installer.ps1" | Invoke-Expression }
        else { curl --proto '=https' --tlsv1.2 -LsSf "https://github.com/astral-sh/uv/releases/download/$Version/uv-installer.sh" | sh }
        Move-Item -Force 'bin/uv.*', 'bin/uvx.*' '.'
        Remove-Item 'bin'
        if ($OrigCargoHome) { $Env:CARGO_HOME = $OrigCargoHome }
    }
}

function Sync-Env {
    <#.SYNOPSIS
    Sync virtual environment and set environment variables.#>

    Param([switch]$High)

    # ? Track environment variables to update `.env` with later
    $EnvVars = @{}
    $EnvPath = $Env:GITHUB_ENV ? $Env:GITHUB_ENV : '.env'
    # ? Create `env` if missing
    if (!($EnvFile = Get-Item $EnvPath -ErrorAction 'Ignore')) {
        New-Item $EnvPath
        $EnvFile = Get-Item $EnvPath
    }

    # ? Sync environment
    $RequirementsDir = Get-Item 'requirements'
    $RequirementsPath = $High ? "$RequirementsDir/requirements_high.txt" : "$RequirementsDir/requirements.txt"
    if ($High) {
        uv sync --resolution highest
        $DefaultLockPath = 'uv.lock'
        Move-Item -Force $DefaultLockPath "$RequirementsDir/uv_high.lock"
        $PostCheckoutPath = '.git/hooks/post-checkout'
        if ($PostCheckoutHook = (Test-Path $PostCheckoutPath)) { Move-Item $PostCheckoutPath .git/hooks/_post-checkout }
        git checkout -- $DefaultLockPath
        if ($PostCheckoutHook) { Move-Item '.git/hooks/_post-checkout' $PostCheckoutPath }
        $LockPath = $High ? "$RequirementsDir/uv_high.lock" : 'uv.lock'
        Move-Item 'uv.lock' $LockPath -Force
        (uv export --no-hashes --resolution highest --output-file $RequirementsPath) |
            Set-Content $RequirementsPath
    }
    else {
        uv sync
        (uv export --no-hashes --output-file $RequirementsPath) |
            Set-Content $RequirementsPath
    }
    if ($IsWindows) { .venv/scripts/activate.ps1 } else { .venv/bin/activate.ps1 }

    # ? Get environment variables from `pyproject.toml`
    dev init-shell |
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
            if ($EnvVars.ContainsKey($Key)) {
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
}
