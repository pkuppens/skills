#requires -Version 7
<#
.SYNOPSIS  Link or overlay a canonical pkuppens/skills skill into ~/.claude/skills.
.PARAMETER Name         Skill folder name under <Repo>/skills.
.PARAMETER Repo         Path to the pkuppens/skills clone.
.PARAMETER Mode         Junction | Symlink | Overlay | Check
.PARAMETER TargetRoot   Skills directory to write into (default ~/.claude/skills).
.PARAMETER OverlayRoot  Where <name>.yaml overlays live (default ~/.claude/skill-overlays).
#>
param(
    [Parameter(Mandatory)][string]$Name,
    [Parameter(Mandatory)][string]$Repo,
    [ValidateSet('Junction', 'Symlink', 'Overlay', 'Check')][string]$Mode = 'Junction',
    [string]$TargetRoot = (Join-Path $HOME '.claude/skills'),
    [string]$OverlayRoot = (Join-Path $HOME '.claude/skill-overlays')
)
$ErrorActionPreference = 'Stop'
$src = Join-Path $Repo "skills/$Name"
$dst = Join-Path $TargetRoot $Name
$overlay = Join-Path $OverlayRoot "$Name.yaml"
if (-not (Test-Path (Join-Path $src 'SKILL.md'))) { throw "No SKILL.md in $src" }

function Get-Norm([string]$p) { (Get-Content -Raw $p) -replace "`r`n", "`n" }

function Build-OverlaySkillMd {
    $text = Get-Norm (Join-Path $src 'SKILL.md')
    $extra = if (Test-Path $overlay) { (Get-Norm $overlay).TrimEnd("`n") } else { '' }
    if (-not $text.StartsWith("---`n")) { throw 'SKILL.md has no frontmatter' }
    $end = $text.IndexOf("`n---`n", 4)
    if ($end -lt 0) { throw 'SKILL.md frontmatter not closed' }
    $head = $text.Substring(0, $end)
    $rest = $text.Substring($end)
    if ($extra) { $head = "$head`n$extra" }
    $head + $rest
}

function Test-IsLink($item) { $item.LinkType -in 'Junction', 'SymbolicLink', 'HardLink' }

if ($Mode -eq 'Check') {
    if (-not (Test-Path $dst)) { Write-Output "DRIFT: $dst does not exist"; exit 1 }
    $item = Get-Item $dst -Force
    if ($item.LinkType -in 'Junction', 'SymbolicLink') {
        $target = @($item.Target)[0]
        if ((Resolve-Path $target).Path -eq (Resolve-Path $src).Path) { Write-Output "OK: $dst -> $src ($($item.LinkType))"; exit 0 }
        Write-Output "DRIFT: $dst points at $target, not $src"; exit 1
    }
    $bad = 0
    if ((Get-Norm (Join-Path $dst 'SKILL.md')) -ne (Build-OverlaySkillMd)) { Write-Output 'DRIFT: SKILL.md differs from canonical+overlay'; $bad = 1 }
    foreach ($d in Get-ChildItem $src -Directory) {
        $t = Join-Path $dst $d.Name
        if (-not (Test-Path $t)) { Write-Output "DRIFT: missing $($d.Name)"; $bad = 1; continue }
        $ti = Get-Item $t -Force
        if ($ti.LinkType -in 'Junction', 'SymbolicLink') {
            if ((Resolve-Path @($ti.Target)[0]).Path -ne $d.FullName) { Write-Output "DRIFT: $($d.Name) links elsewhere"; $bad = 1 }
        } else { Write-Output "DRIFT: $($d.Name) is a plain copy, not a link"; $bad = 1 }
    }
    foreach ($f in Get-ChildItem $src -File | Where-Object Name -ne 'SKILL.md') {
        $t = Join-Path $dst $f.Name
        if (-not (Test-Path $t) -or (Get-Norm $t) -ne (Get-Norm $f.FullName)) { Write-Output "DRIFT: $($f.Name) missing or different"; $bad = 1 }
    }
    if (-not $bad) { Write-Output "OK: $dst (overlay) matches canonical" }
    exit $bad
}

New-Item -ItemType Directory -Force $TargetRoot | Out-Null
if (Test-Path $dst) {
    $it = Get-Item $dst -Force
    if ($it.LinkType -in 'Junction', 'SymbolicLink') { $it.Delete() }   # removes the link only, never the target contents
    else { Move-Item $dst "$dst.bak-$(Get-Date -Format yyyyMMddHHmmss)" }
}

switch ($Mode) {
    'Junction' { New-Item -ItemType Junction -Path $dst -Target (Resolve-Path $src).Path | Out-Null }
    'Symlink' { New-Item -ItemType SymbolicLink -Path $dst -Target (Resolve-Path $src).Path | Out-Null }
    'Overlay' {
        New-Item -ItemType Directory $dst | Out-Null
        foreach ($d in Get-ChildItem $src -Directory) {
            New-Item -ItemType Junction -Path (Join-Path $dst $d.Name) -Target $d.FullName | Out-Null
        }
        foreach ($f in Get-ChildItem $src -File | Where-Object Name -ne 'SKILL.md') {
            New-Item -ItemType HardLink -Path (Join-Path $dst $f.Name) -Target $f.FullName | Out-Null
        }
        [IO.File]::WriteAllText((Join-Path $dst 'SKILL.md'), (Build-OverlaySkillMd))
    }
}
Write-Output "Linked ($Mode): $dst <- $src"
