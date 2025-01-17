<#.SYNOPSIS
Common utilities.#>

# ? Error-handling
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $True
$ErrorView = 'NormalView'

# ? Fix leaky UTF-8 encoding settings on Windows
if ($IsWindows) {
    # ? Now PowerShell pipes will be UTF-8. Note that fixing it from Control Panel and
    # ? system-wide has buggy downsides.
    # ? See: https://github.com/PowerShell/PowerShell/issues/7233#issuecomment-640243647
    [console]::InputEncoding = [console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
}

# ? Set aliases
@{
    'iuv' = 'Invoke-Uv'
    'ij' = 'Invoke-Just'
    'dev' = 'boilercv-dev'
    'pipeline' = 'boilercv-pipeline'
}.GetEnumerator() | ForEach-Object { Set-Alias -Name $_.Key -Value $_.Value }

function Enter-Venv {
    <#.SYNOPSIS
    Enter a local Python virtual environment.#>
    if ($IsWindows) { .venv/scripts/activate.ps1 } else { .venv/bin/activate.ps1 }
}

function Initialize-Shell {
    <#.SYNOPSIS
    Initialize shell.#>
    if (!(Test-Path '.venv')) { Invoke-Uv -Sync -Update -Force }
    Enter-Venv
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

function Install-Uv {
    <#.SYNOPSIS
    Install `uv`.#>
    Param(
        [switch]$Update,
        [string]$UvVersion = (Get-Content '.uv-version')
    )
    $Env:PATH = "$HOME/.cargo/bin$([System.IO.Path]::PathSeparator)$Env:PATH"
    if ($Update) {
        if (Get-Command 'uv' -ErrorAction 'Ignore') {
            try { return uv self update $UvVersion }
            catch [System.Management.Automation.NativeCommandExitException] {}
        }
        if ($IsWindows) { Invoke-RestMethod 'https://astral.sh/uv/install.ps1' | Invoke-Expression }
        else { curl --proto '=https' --tlsv1.2 -LsSf 'https://astral.sh/uv/install.sh' | sh }
    }
}

function New-Switch {
    Param($Cond = $False, $Alt = $False)
    return [switch]($Cond ? $True : $Alt)
}

function Invoke-Uv {
    <#.SYNOPSIS
    Invoke `uv`.#>
    [CmdletBinding(PositionalBinding = $False)]
    Param(
        [switch]$Sync,
        [switch]$Update,
        [switch]$Low,
        [switch]$High,
        [switch]$Build,
        [switch]$Force,
        [switch]$CI = (New-Switch $Env:SYNC_ENV_DISABLE_CI (New-Switch $Env:CI)),
        [switch]$Locked = $CI,
        [switch]$Devcontainer = (New-Switch $Env:SYNC_ENV_DISABLE_DEVCONTAINER (New-Switch $Env:DEVCONTAINER)),
        [string]$PythonVersion = (Get-Content '.python-version'),
        [string]$PylanceVersion = (Get-Content '.pylance-version'),
        [Parameter(ValueFromPipeline, ValueFromRemainingArguments)][string[]]$Run
    )
    Begin {
        if (!$CI) {
            # ? Install or update `uv`
            if ($Update -or !(Get-Command 'uv' -ErrorAction 'Ignore')) { Install-Uv -Update }
            else { Install-Uv }
            # ? Sync submodules
            Get-ChildItem '.git/modules' -Filter 'config.lock' -Recurse -Depth 1 |
                Remove-Item
            git submodule update --init --merge
        }
        if ($CI -or $Sync) {
            # ? Sync the environment
            if (!(Test-Path 'requirements')) {
                New-Item 'requirements' -ItemType 'Directory'
            }
            $LockedArg = $Locked ? '--locked' : $null
            $FrozenArg = $Locked ? $null : '--frozen'
            if ($Low) {
                uv sync $LockedArg --resolution lowest-direct --python $PythonVersion
                uv export $LockedArg $FrozenArg --resolution lowest-direct --no-hashes --python $PythonVersion |
                    Set-Content "$PWD/requirements/requirements_dev_low.txt"
                $Env:ENV_SYNCED = $null
                Enter-Venv
            }
            elseif ($High) {
                uv sync $LockedArg --upgrade --python $PythonVersion
                uv export $LockedArg $FrozenArg --no-hashes --python $PythonVersion |
                    Set-Content "$PWD/requirements/requirements_dev_high.txt"
                $Env:ENV_SYNCED = $null
                Enter-Venv
            }
            elseif ($Build) {
                $LockedArg = $null
                $FrozenArg = '--frozen'
                uv sync $LockedArg --no-sources --no-dev --python $PythonVersion
                uv export $LockedArg $FrozenArg --no-dev --no-hashes --python $PythonVersion |
                    Set-Content "$PWD/requirements/requirements_prod.txt"
                uv build --python $PythonVersion
                $Env:ENV_SYNCED = $null
                Enter-Venv
            }
            elseif ($CI -or $Force -or !$Env:ENV_SYNCED) {
                # ? Sync the environment
                uv sync $LockedArg --python $PythonVersion
                uv export $LockedArg $FrozenArg --no-hashes --python $PythonVersion |
                    Set-Content "$PWD/requirements/requirements_dev.txt"
                if ($CI) {
                    Add-Content $Env:GITHUB_PATH ("$PWD/.venv/bin", "$PWD/.venv/scripts")
                }
                $Env:ENV_SYNCED = $True
                Enter-Venv

                # ? Sync `.env` and set environment variables from `pyproject.toml`
                $EnvVars = boilercv-dev 'sync-environment-variables'
                $EnvVars | Set-Content ($Env:GITHUB_ENV ? $Env:GITHUB_ENV : "$PWD/.env")
                $EnvVars | Select-String -Pattern '^(.+?)=(.+)$' | ForEach-Object {
                    $Key, $Value = $_.Matches.Groups[1].Value, $_.Matches.Groups[2].Value
                    Set-Item "Env:$Key" $Value
                }

                # ? Environment-specific setup
                if ($CI) { boilercv-dev 'elevate-pyright-warnings' }
                elseif ($Devcontainer) {
                    $Repo = Get-ChildItem '/workspaces'
                    $Packages = Get-ChildItem "$Repo/packages"
                    $SafeDirs = @($Repo) + $Packages
                    foreach ($Dir in $SafeDirs) {
                        if (!($SafeDirs -contains $Dir)) {
                            git config --global --add safe.directory $Dir
                        }
                    }
                }

                # ? Install pre-commit hooks
                else {
                    $Hooks = '.git/hooks'
                    if (
                        !(Test-Path "$Hooks/pre-commit") -or
                        !(Test-Path "$Hooks/post-checkout")
                    ) { uv run --no-sync --python $PythonVersion pre-commit install --install-hooks }
                    if (!$Devcontainer -and (Get-Command -Name 'code' -ErrorAction 'Ignore')) {
                        $LocalExtensions = '.vscode/extensions'
                        $Pylance = 'ms-python.vscode-pylance'
                        if (!(Test-Path "$LocalExtensions/$Pylance-$PylanceVersion")) {
                            $Install = @(
                                "--extensions-dir=$LocalExtensions",
                                "--install-extension=$Pylance@$PylanceVersion"
                            )
                            code @Install
                            if (Test-Path $LocalExtensions) {
                                $PylanceExtension = (
                                    Get-ChildItem -Path $LocalExtensions -Filter "$Pylance-*"
                                )
                                # ? Remove other files
                                Get-ChildItem -Path $LocalExtensions |
                                    Where-Object { Compare-Object $_ $PylanceExtension } |
                                    Remove-Item -Recurse
                                # ? Remove local Pylance bundled stubs
                                $PylanceExtension | ForEach-Object {
                                    Get-ChildItem "$_/dist/bundled" -Filter '*stubs'
                                } | Remove-Item -Recurse
                            }
                        }
                    }
                }
            }
        }
    }
    Process { if ($Run) { uv run --no-sync --python $PythonVersion $Run } }
}

function Invoke-Just {
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
        [switch]$CI,
        [switch]$Locked,
        [switch]$Devcontainer,
        [string]$PythonVersion = (Get-Content '.python-version'),
        [string]$PylanceVersion = (Get-Content '.pylance-version'),
        [Parameter(ValueFromPipeline, ValueFromRemainingArguments)][string[]]$Run
    )
    Begin {
        $CI = (New-Switch $Env:SYNC_ENV_DISABLE_CI (New-Switch $Env:CI))
        $InvokeUvArgs = @{
            Sync           = $Sync
            Update         = $Update
            Low            = $Low
            High           = $High
            Build          = $Build
            Force          = $Force
            CI             = $CI
            Locked         = $CI
            Devcontainer   = (New-Switch $Env:SYNC_ENV_DISABLE_DEVCONTAINER (New-Switch $Env:DEVCONTAINER))
            PythonVersion  = $PythonVersion
            PylanceVersion = $PylanceVersion
        }
        if (!(Get-Command 'just' -ErrorAction 'Ignore')) { Initialize-Shell }
    }
    Process { if ($Run) { Invoke-Uv @InvokeUvArgs -- just @Run } else { Invoke-Uv @InvokeUvArgs -- just } }
}

function Sync-Template {
    <#.SYNOPSIS
    Sync with template.#>
    Param(
        # Specific template VCS reference.
        [string]$Ref = 'HEAD',
        # Prompt for new answers.
        [switch]$Prompt,
        # Recopy, ignoring prior diffs instead of a smart update.
        [switch]$Recopy,
        # Stay on the current template version when updating.
        [switch]$Stay
    )
    if (!(Get-Command 'uv' -ErrorAction 'Ignore')) { Install-Uv -Update }
    $Copier = "copier@$(Get-Content '.copier-version')"
    $Ref = $Stay ? (Get-Content '.copier-answers.yml' | Find-Pattern '^_commit:\s.+-(.+)$') : $Ref
    if ($Recopy) {
        if ($Prompt) { return uvx $Copier recopy $Defaults --vcs-ref=$Ref }
        return uvx $Copier recopy --overwrite --defaults
    }
    if ($Prompt) { return uvx $Copier update --vcs-ref=$Ref }
    return uvx $Copier update --defaults --vcs-ref=$Ref
}

function Initialize-Repo {
    <#.SYNOPSIS
    Initialize repository.#>

    git init

    # ? Modify GitHub repo later on only if there were not already commits in this repo
    try { git rev-parse HEAD }
    catch [System.Management.Automation.NativeCommandExitException] { $Fresh = $True }

    git add .
    try { git commit --no-verify -m 'Prepare template using blakeNaccarato/copier-python' }
    catch [System.Management.Automation.NativeCommandExitException] {}

    git submodule add --force --name 'typings' 'https://github.com/microsoft/python-type-stubs.git' 'typings'
    git add .
    try { git commit --no-verify -m 'Add template and type stub submodules' }
    catch [System.Management.Automation.NativeCommandExitException] {}

    Initialize-Shell

    git add .
    try { git commit --no-verify -m 'Lock' }
    catch [System.Management.Automation.NativeCommandExitException] {}

    # ? Modify GitHub repo if there were not already commits in this repo
    if ($Fresh) {
        if (!(git remote)) {
            git remote add origin 'https://github.com/softboiler/boilercv.git'
            git branch --move --force main
        }
        gh repo edit --description (
            Get-Content '.copier-answers.yml' |
                Find-Pattern '^project_description:\s(.+)$'
        )
        gh repo edit --homepage 'https://softboiler.github.io/boilercv/'
    }

    git push --set-upstream origin main
}


function Initialize-Machine {
    <#.SYNOPSIS
    Finish machine initialization (cross-platform).#>

    Param([switch]$Force)

    # ? Hook into user profile if it doesn't exist already
    if ($Force -or !(Test-Path $PROFILE)) {
        if (!(Test-Path $PROFILE)) { New-Item $PROFILE }
        'if (Test-Path ''dev.ps1'') { . ./dev.ps1 && Initialize-Shell }' |
            Add-Content $PROFILE
    }

    # ? Set Git username if missing
    try { $Name = git config 'user.name' }
    catch [System.Management.Automation.NativeCommandExitException] { $Name = '' }
    if ($Force -or !$Name) {
        Write-Output 'Username missing from `.gitconfig`. Prompting for GitHub username/email ...'
        $Ans = Read-Host -Prompt 'Enter your GitHub username'
        if ($Ans) { git config --global 'user.name' $Ans }
        git config --global fetch.prune true
        git config --global pull.rebase true
        git config --global push.autoSetupRemote true
        git config --global push.followTags true

        # ? Set Git email if missing
        try { $Email = git config 'user.email' }
        catch [System.Management.Automation.NativeCommandExitException] { $Email = '' }
        if ($Force -or !$Email) {
            $Ans = Read-Host -Prompt 'Enter the email address associated with your GitHub account'
            if ($Ans) { git config --global 'user.email' $Ans }
        }
    }
    # ? Log in to GitHub API
    if ($Force -or !(gh auth status)) { gh auth login -Done }
}

function Initialize-Windows {
    <#.SYNOPSIS
    Initialize Windows machine.#>

    $origPreference = $ErrorActionPreference
    $ErrorActionPreference = 'SilentlyContinue'

    # ? Install and update `uv`
    Install-Uv -Update

    # ? Common winget options
    $Install = @(
        'install',
        '--accept-package-agreements',
        '--accept-source-agreements',
        '--disable-interactivity'
        '--exact',
        '--no-upgrade',
        '--silent',
        '--source=winget'
    )

    # ? Install PowerShell Core
    winget @Install --id='Microsoft.PowerShell' --override='/quiet ADD_EXPLORER_CONTEXT_MENU_OPENPOWERSHELL=1 ADD_FILE_CONTEXT_MENU_RUNPOWERSHELL=1 ADD_PATH=1 ENABLE_MU=1 ENABLE_PSREMOTING=1 REGISTER_MANIFEST=1 USE_MU=1'
    # ? Set Windows PowerShell execution policy
    powershell -Command 'Set-ExecutionPolicy -Scope CurrentUser RemoteSigned'
    # ? Set PowerShell Core execution policy
    pwsh -Command 'Set-ExecutionPolicy -Scope CurrentUser RemoteSigned'

    # ? Install VSCode
    winget @Install --id='Microsoft.VisualStudioCode'
    # ? Install Windows Terminal
    winget @Install --id='Microsoft.WindowsTerminal'
    # ? Install GitHub CLI
    winget @Install --id='GitHub.cli'

    # ? Install git
    @'
[Setup]
Lang=default
Dir=C:/Program Files/Git
Group=Git
NoIcons=0
SetupType=default
Components=ext,ext\shellhere,ext\guihere,gitlfs,assoc,assoc_sh,autoupdate,windowsterminal,scalar
Tasks=
EditorOption=VisualStudioCode
CustomEditorPath=
DefaultBranchOption=main
PathOption=Cmd
SSHOption=OpenSSH
TortoiseOption=false
CURLOption=OpenSSL
CRLFOption=CRLFAlways
BashTerminalOption=MinTTY
GitPullBehaviorOption=Merge
UseCredentialManager=Enabled
PerformanceTweaksFSCache=Enabled
EnableSymlinks=Disabled
EnablePseudoConsoleSupport=Disabled
EnableFSMonitor=Enabled
'@ | Out-File ($inf = New-TemporaryFile)
    winget @Install --id='Git.Git' --override="/SILENT /LOADINF=$inf"
    $ErrorActionPreference = $origPreference

    # ? Finish machine setup
    Initialize-Machine
}
