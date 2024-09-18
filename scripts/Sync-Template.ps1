<#.SYNOPSIS
Sync with template.#>
Param(
    # Specific template VCS reference.
    [Parameter(ValueFromPipeline)]$Ref,
    # Prompt for new answers.
    [switch]$Prompt,
    # Recopy, ignoring prior diffs instead of a smart update.
    [switch]$Recopy,
    # Stay on the current template version when updating.
    [switch]$Stay
)
begin {
    . scripts/Common.ps1
    $Copier = 'copier@9.2.0'
}
process {
    if (!$Stay) {
        git submodule update --init --remote --merge $Template
        git add .
        $Ref = $Ref ? $Ref : (Get-Content '.copier-answers.yml' | Find-Pattern '^_commit:\s.+([^-]+)$')
        try { git commit --no-verify -m "Update template digest to $Ref" }
        catch [System.Management.Automation.NativeCommandExitException] { $AlreadyUpdated = $true }
    }
    # ? Get latest ref
    $Ref = $Ref ? $Ref : (Get-Content '.copier-answers.yml' | Find-Pattern '^_commit:\s.+([^-]+)$')
    if ($Recopy) {
        if ($Prompt) { return uvx $Copier $Subcommand $Defaults --vcs-ref=$Ref }
        return uvx $Copier recopy --overwrite --defaults --vcs-ref=$Ref
    }
    if ($Prompt) { return uvx $Copier update --vcs-ref=$Ref }
    return uvx $Copier update --defaults --vcs-ref=$Ref
}
