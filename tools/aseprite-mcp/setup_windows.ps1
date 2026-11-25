<#
.SYNOPSIS
  aseprite-mcp (diivi/aseprite-mcp) 설치 / Install aseprite-mcp for Claude on Windows.

.DESCRIPTION
  여러 번 실행해도 안전합니다 (idempotent). 관리자 권한이 필요 없습니다.
  Safe to run again. No administrator rights needed.

  1. git 확인, uv 확인 (없으면 공식 설치 스크립트로 설치)
  2. diivi/aseprite-mcp 를 %USERPROFILE%\tools\aseprite-mcp 에 받아 검토한 커밋으로 고정
  3. Aseprite.exe 찾기 -> .env (ASEPRITE_PATH, ASEPRITE_TIMEOUT_SECONDS) 작성
  4. uv sync (잠금 파일 그대로) + 자체 시험 (import, aseprite --version)
  5. Claude Code 에 등록 (claude mcp add --scope user) + 위험한 도구 5개 deny 규칙
  6. -Desktop 을 주면 Claude Desktop 설정(claude_desktop_config.json)에도 추가 (백업 후)

  This script never stores secrets and never calls any MCP tool (run_lua_script included).

.PARAMETER AsepritePath
  Aseprite.exe 의 전체 경로 (자동으로 못 찾을 때). Full path to Aseprite.exe if auto-detection fails.
.PARAMETER InstallDir
  설치 폴더. Default: %USERPROFILE%\tools\aseprite-mcp
.PARAMETER Desktop
  Claude Desktop 채팅용 설정 파일에도 추가. Also add the server to claude_desktop_config.json.
.PARAMETER AllowReadOnly
  읽기 전용 도구(픽셀 읽기, 정보 보기)를 묻지 않고 허용하는 allow 규칙도 추가.
.PARAMETER SkipClaudeCode
  Claude Code 등록과 settings.json 수정을 건너뜀.
.PARAMETER ClaudeExe
  claude 명령의 전체 경로 (PATH 에 없을 때).
.PARAMETER TimeoutSeconds
  Aseprite 한 번 실행의 제한 시간 (기본 60).
.PARAMETER Uninstall
  등록 해제 (Claude Code + Desktop 설정). -RemoveFiles 를 같이 주면 설치 폴더도 지움.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\tools\aseprite-mcp\setup_windows.ps1
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\tools\aseprite-mcp\setup_windows.ps1 -AsepritePath "D:\Games\Aseprite\Aseprite.exe" -Desktop
#>
[CmdletBinding()]
param(
    [string]$AsepritePath = '',
    [string]$InstallDir = '',
    [switch]$Desktop,
    [switch]$AllowReadOnly,
    [switch]$SkipClaudeCode,
    [string]$ClaudeExe = '',
    [ValidateRange(1, 3600)]
    [int]$TimeoutSeconds = 60,
    [switch]$Uninstall,
    [switch]$RemoveFiles
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false } catch { }

# ---------------------------------------------------------------------------
# Reviewed version (read-only security review 2026-11-25). Do not change without a new review.
# ---------------------------------------------------------------------------
$RepoUrl      = 'https://github.com/diivi/aseprite-mcp.git'
$PinnedCommit = '4bcdb6f5932116bbdbd1b7d3fcc1e8f965f7657a'
$ServerName   = 'aseprite'

# Tools denied by the review: raw Lua (shell / file access), two tools with a Lua-injection bug,
# and the preview HTTP server (listens on all interfaces, force-kills a PID from a temp file).
$DenyTools = @(
    'mcp__aseprite__run_lua_script',
    'mcp__aseprite__audit_animation',
    'mcp__aseprite__animation_sanitize',
    'mcp__aseprite__start_preview_server',
    'mcp__aseprite__stop_preview_server'
)
# Read-only tools the review considers safe to auto-allow (only with -AllowReadOnly).
# Built with a foreach statement + [string[]] so the JSON writer sees plain strings.
[string[]]$ReadOnlyTools = foreach ($n in @(
    'get_sprite_info', 'get_pixel_color', 'get_pixels_rect', 'get_composite_pixel', 'get_composite_rect',
    'read_rows', 'view_sprite', 'list_slices', 'get_tile_at', 'get_tilemap_info', 'get_palette',
    'list_palette_presets', 'list_convolution_matrices', 'list_text_fonts', 'measure_text', 'compare_frames',
    'get_bounds', 'get_color_stats', 'lint_sprite', 'animation_workflow_guide'
)) { 'mcp__aseprite__' + $n }

if (-not $InstallDir) { $InstallDir = Join-Path $env:USERPROFILE 'tools\aseprite-mcp' }
# Absolute path: it is written into the Claude config, where a relative path would break.
$InstallDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($InstallDir)
$InstallDir = $InstallDir.TrimEnd('\', '/')

# Claude Code reads user settings from CLAUDE_CONFIG_DIR when it is set, else %USERPROFILE%\.claude.
$ClaudeConfigDir = Join-Path $env:USERPROFILE '.claude'
if ($env:CLAUDE_CONFIG_DIR) { $ClaudeConfigDir = $env:CLAUDE_CONFIG_DIR }

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
function Say([string]$ko, [string]$en) { Write-Host "  $ko" ; if ($en) { Write-Host "    ($en)" -ForegroundColor DarkGray } }
function Step([string]$ko, [string]$en) { Write-Host '' ; Write-Host "== $ko / $en" -ForegroundColor Cyan }
function Ok([string]$msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Warn([string]$ko, [string]$en) { Write-Host "  [주의] $ko" -ForegroundColor Yellow ; if ($en) { Write-Host "    (warning: $en)" -ForegroundColor Yellow } }
function Fail([string]$ko, [string]$en) {
    Write-Host ''
    Write-Host "  [실패] $ko" -ForegroundColor Red
    if ($en) { Write-Host "    (failed: $en)" -ForegroundColor Red }
    exit 1
}

# Runs a native program without letting PowerShell 5.1 turn its stderr into a terminating error.
function Invoke-Native {
    param([string]$Exe, [string[]]$ArgList = @(), [switch]$Quiet)
    $ErrorActionPreference = 'Continue'
    $out = & $Exe @ArgList 2>&1 | ForEach-Object { "$_" }
    $code = $LASTEXITCODE
    if (-not $Quiet) { foreach ($line in $out) { Write-Host "    $line" -ForegroundColor DarkGray } }
    return [pscustomobject]@{ Code = $code; Output = (@($out) -join "`n") }
}

function Write-Utf8NoBom([string]$Path, [string]$Text) {
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    [System.IO.File]::WriteAllText($Path, $Text, (New-Object System.Text.UTF8Encoding $false))
}

function Backup-File([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $bak = "$Path.bak-$stamp"
        Copy-Item -LiteralPath $Path -Destination $bak -Force
        Say "백업: $bak" "backup written"
    }
}

# Reads a JSON file into a PSCustomObject. Returns $null (and explains) when the file cannot be parsed.
function Read-JsonFile([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return [pscustomobject]@{} }
    $raw = [System.IO.File]::ReadAllText($Path)
    if (-not $raw.Trim()) { return [pscustomobject]@{} }
    try { return ($raw | ConvertFrom-Json) }
    catch {
        Warn "JSON 을 읽을 수 없어 건드리지 않았습니다: $Path" "could not parse JSON, file left unchanged"
        return $null
    }
}

function Get-OrAddObject($Parent, [string]$Name) {
    $p = $Parent.PSObject.Properties[$Name]
    if (-not $p -or $null -eq $p.Value -or -not ($p.Value -is [System.Management.Automation.PSCustomObject])) {
        $Parent | Add-Member -NotePropertyName $Name -NotePropertyValue ([pscustomobject]@{}) -Force
    }
    return $Parent.PSObject.Properties[$Name].Value
}

function Find-Uv {
    $c = Get-Command uv -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    foreach ($p in @((Join-Path $env:USERPROFILE '.local\bin\uv.exe'), (Join-Path $env:USERPROFILE '.cargo\bin\uv.exe'),
                     (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links\uv.exe'))) {
        if (Test-Path -LiteralPath $p) { return $p }
    }
    # winget package folder (when the Links shim is missing)
    $pk = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'
    if (Test-Path -LiteralPath $pk) {
        $f = Get-ChildItem -LiteralPath $pk -Filter 'uv.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($f) { return $f.FullName }
    }
    return $null
}

function Find-Claude {
    if ($ClaudeExe) {
        if (Test-Path -LiteralPath $ClaudeExe) { return (Resolve-Path -LiteralPath $ClaudeExe).Path }
        Warn "-ClaudeExe 경로가 없습니다: $ClaudeExe" "claude not found at -ClaudeExe"
        return $null
    }
    # Prefer claude.exe / claude.cmd (CommandType Application) over npm's claude.ps1 shim:
    # PowerShell removes a literal "--" from the arguments of a .ps1 script, which breaks "claude mcp add ... -- uv ...".
    $c = Get-Command claude -CommandType Application -ErrorAction SilentlyContinue |
        Where-Object { $_.Source -match '\.(exe|cmd)$' } | Select-Object -First 1
    if ($c) { return $c.Source }
    $p = Join-Path $env:USERPROFILE '.local\bin\claude.exe'
    if (Test-Path -LiteralPath $p) { return $p }
    return $null
}

function Get-DesktopConfigPaths {
    $paths = @()
    $roaming = Join-Path $env:APPDATA 'Claude'
    if (Test-Path -LiteralPath $roaming) { $paths += (Join-Path $roaming 'claude_desktop_config.json') }
    $pkgRoot = Join-Path $env:LOCALAPPDATA 'Packages'
    if (Test-Path -LiteralPath $pkgRoot) {
        Get-ChildItem -LiteralPath $pkgRoot -Directory -Filter 'Claude_*' -ErrorAction SilentlyContinue | ForEach-Object {
            $d = Join-Path $_.FullName 'LocalCache\Roaming\Claude'
            if (Test-Path -LiteralPath $d) { $paths += (Join-Path $d 'claude_desktop_config.json') }
        }
    }
    if ($paths.Count -eq 0) { $paths += (Join-Path $roaming 'claude_desktop_config.json') }
    return $paths
}

function Find-Aseprite {
    $found = New-Object System.Collections.Generic.List[string]
    $add = {
        param($p)
        if ($p -and (Test-Path -LiteralPath $p -PathType Leaf)) {
            $full = (Resolve-Path -LiteralPath $p).ProviderPath
            # -contains is case-insensitive (Steam's registry path is lower case).
            if (-not ($found -contains $full)) { $found.Add($full) }
        }
    }
    $pf = $env:ProgramFiles
    $pf86 = ${env:ProgramFiles(x86)}
    foreach ($base in @($pf, $pf86)) {
        if ($base) {
            & $add (Join-Path $base 'Aseprite\Aseprite.exe')
            & $add (Join-Path $base 'Steam\steamapps\common\Aseprite\Aseprite.exe')
        }
    }
    if ($env:LOCALAPPDATA) {
        & $add (Join-Path $env:LOCALAPPDATA 'Programs\Aseprite\Aseprite.exe')
        & $add (Join-Path $env:LOCALAPPDATA 'Aseprite\Aseprite.exe')
    }
    # Other Steam libraries (libraryfolders.vdf)
    $steamRoots = @()
    try {
        $reg = Get-ItemProperty -Path 'HKCU:\Software\Valve\Steam' -ErrorAction Stop
        if ($reg.SteamPath) { $steamRoots += ($reg.SteamPath -replace '/', '\') }
    } catch { }
    if ($pf86) { $steamRoots += (Join-Path $pf86 'Steam') }
    if ($pf) { $steamRoots += (Join-Path $pf 'Steam') }
    foreach ($root in ($steamRoots | Select-Object -Unique)) {
        $vdf = Join-Path $root 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf) {
            foreach ($m in [regex]::Matches([System.IO.File]::ReadAllText($vdf), '"path"\s+"([^"]+)"')) {
                $lib = $m.Groups[1].Value -replace '\\\\', '\'
                & $add (Join-Path $lib 'steamapps\common\Aseprite\Aseprite.exe')
            }
        }
    }
    $c = Get-Command aseprite -ErrorAction SilentlyContinue
    if ($c -and $c.Source) { & $add $c.Source }
    return ,$found
}

function Test-AsepriteVersion([string]$Exe) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Exe
    $psi.Arguments = '--batch --version'
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    try { $p = [System.Diagnostics.Process]::Start($psi) }
    catch { Warn "Aseprite 를 실행하지 못했습니다: $($_.Exception.Message)" 'could not start Aseprite'; return $null }
    $o = $p.StandardOutput.ReadToEndAsync()
    $e = $p.StandardError.ReadToEndAsync()
    if (-not $p.WaitForExit(60000)) {
        try { $p.Kill() } catch { }
        return $null
    }
    # A process started by Aseprite (e.g. a Steam relaunch) can inherit the pipes and keep them open:
    # wait a few seconds for the output, never forever.
    $text = ''
    if ($o.Wait(5000)) { $text += $o.Result }
    if ($e.Wait(1000)) { $text += ' ' + $e.Result }
    return $text.Trim()
}

# ---------------------------------------------------------------------------
# Uninstall
# ---------------------------------------------------------------------------
if ($Uninstall) {
    Step '등록 해제' 'Uninstall'
    if (-not $SkipClaudeCode) {
        $claude = Find-Claude
        if ($claude) {
            $r = Invoke-Native $claude @('mcp', 'remove', $ServerName, '--scope', 'user') -Quiet
            if ($r.Code -eq 0) { Ok 'Claude Code 에서 aseprite 등록을 지웠습니다 (removed from Claude Code)' }
            else { Say 'Claude Code 에 user 범위 aseprite 등록이 없었습니다' 'no user-scope registration found' }
        } else {
            Say 'claude 명령이 없어 Claude Code 등록 해제를 건너뜁니다' 'claude not on PATH; skipped'
        }
        Say "deny 규칙($($DenyTools.Count)개)은 그대로 둡니다 (서버가 없으면 아무 영향 없음)." 'deny rules are left in place; harmless without the server'
    }
    foreach ($cfgPath in (Get-DesktopConfigPaths)) {
        if (Test-Path -LiteralPath $cfgPath) {
            $cfg = Read-JsonFile $cfgPath
            if ($cfg -and $cfg.PSObject.Properties['mcpServers'] -and $cfg.mcpServers -and $cfg.mcpServers.PSObject.Properties[$ServerName]) {
                Backup-File $cfgPath
                $cfg.mcpServers.PSObject.Properties.Remove($ServerName)
                Write-Utf8NoBom $cfgPath ($cfg | ConvertTo-Json -Depth 64)
                Ok "Claude Desktop 설정에서 지웠습니다: $cfgPath"
            }
        }
    }
    if ($RemoveFiles) {
        if ((Test-Path -LiteralPath $InstallDir) -and ((Split-Path -Leaf $InstallDir) -eq 'aseprite-mcp')) {
            Remove-Item -LiteralPath $InstallDir -Recurse -Force
            Ok "설치 폴더를 지웠습니다: $InstallDir"
        } else {
            Warn "설치 폴더를 지우지 않았습니다 (없거나 이름이 aseprite-mcp 가 아님): $InstallDir" 'install folder not removed'
        }
    } else {
        Say "설치 폴더는 남겨 두었습니다: $InstallDir  (지우려면 -Uninstall -RemoveFiles)" 'files kept; add -RemoveFiles to delete them'
    }
    Say 'Claude 앱(또는 claude 세션)을 다시 시작하세요.' 'restart Claude'
    exit 0
}

Write-Host ''
Write-Host 'aseprite-mcp 설치 (pixel-management 프로젝트용)' -ForegroundColor White
Write-Host "  설치 폴더 / install dir : $InstallDir"
Write-Host "  고정 커밋 / pinned commit: $PinnedCommit"

# ---------------------------------------------------------------------------
# 1. git
# ---------------------------------------------------------------------------
Step '1/6 git 확인' 'check git'
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Fail ('git 이 없습니다. Git for Windows 를 설치한 뒤 PowerShell 을 새로 열고 다시 실행하세요.' +
          "`n    설치: https://git-scm.com/download/win  또는  winget install --id Git.Git -e") 'git is not installed'
}
$git = $git.Source
Ok "git: $git"

# ---------------------------------------------------------------------------
# 2. uv
# ---------------------------------------------------------------------------
Step '2/6 uv 확인' 'check uv (Python package manager)'
$uv = Find-Uv
if (-not $uv) {
    Say 'uv 가 없어 공식 설치 스크립트(astral.sh)로 설치합니다. 관리자 권한은 필요 없습니다.' 'installing uv with the official installer'
    $ErrorActionPreference = 'Continue'
    & powershell -NoProfile -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $ErrorActionPreference = 'Stop'
    $env:Path = (Join-Path $env:USERPROFILE '.local\bin') + ';' + $env:Path
    $uv = Find-Uv
    if (-not $uv -and (Get-Command winget -ErrorAction SilentlyContinue)) {
        Warn 'astral.sh 설치가 안 되어 winget 으로 다시 시도합니다 (GitHub 에서 받음).' 'astral.sh failed; trying winget (downloads from GitHub)'
        $ErrorActionPreference = 'Continue'
        & winget install --id astral-sh.uv -e --source winget --accept-package-agreements --accept-source-agreements
        $ErrorActionPreference = 'Stop'
        $env:Path = (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links') + ';' + $env:Path
        $uv = Find-Uv
    }
    if (-not $uv) { Fail ('uv 설치에 실패했습니다. 수동 설치 후 새 PowerShell 창에서 다시 실행하세요:' +
                          "`n    winget install --id astral-sh.uv -e --source winget") 'uv install failed' }
}
$uvVer = Invoke-Native $uv @('--version') -Quiet
Ok "uv: $uv ($($uvVer.Output))"

# ---------------------------------------------------------------------------
# 3. clone + pin
# ---------------------------------------------------------------------------
Step '3/6 aseprite-mcp 받기 + 검토한 커밋으로 고정' 'clone and pin the reviewed commit'
if (Test-Path -LiteralPath $InstallDir) {
    if (-not (Test-Path -LiteralPath (Join-Path $InstallDir '.git'))) {
        Fail "폴더가 이미 있지만 git 저장소가 아닙니다: $InstallDir (다른 이름을 -InstallDir 로 주거나 폴더를 옮기세요)" 'folder exists and is not a git clone'
    }
    $remote = (Invoke-Native $git @('-C', $InstallDir, 'remote', 'get-url', 'origin') -Quiet).Output.Trim()
    if ($remote -notmatch 'github\.com[/:]diivi/aseprite-mcp(\.git)?$') {
        Fail "이 폴더의 origin 이 diivi/aseprite-mcp 가 아닙니다: $remote" 'unexpected origin remote'
    }
    # A clone made with --no-checkout has no index until the first checkout (an earlier run stopped there);
    # "git status" would then list every file as deleted, so only check a clone that was checked out.
    $dirty = ''
    if (Test-Path -LiteralPath (Join-Path $InstallDir '.git\index')) {
        $dirty = (Invoke-Native $git @('-C', $InstallDir, 'status', '--porcelain', '--untracked-files=no') -Quiet).Output.Trim()
    }
    if ($dirty) {
        Fail "설치 폴더의 파일이 고쳐져 있습니다. 고친 내용을 확인한 뒤 되돌리세요 (git -C `"$InstallDir`" status)." 'local modifications in the clone'
    }
    Say '이미 받아 둔 폴더를 씁니다.' 'existing clone found'
} else {
    $parent = Split-Path -Parent $InstallDir
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    $r = Invoke-Native $git @('clone', '--no-checkout', $RepoUrl, $InstallDir)
    if ($r.Code -ne 0) { Fail 'git clone 에 실패했습니다. 인터넷 연결을 확인하세요.' 'git clone failed' }
}
$has = Invoke-Native $git @('-C', $InstallDir, 'cat-file', '-e', "$PinnedCommit^{commit}") -Quiet
if ($has.Code -ne 0) {
    $r = Invoke-Native $git @('-C', $InstallDir, 'fetch', 'origin')
    if ($r.Code -ne 0) { Fail 'git fetch 에 실패했습니다.' 'git fetch failed' }
    $has = Invoke-Native $git @('-C', $InstallDir, 'cat-file', '-e', "$PinnedCommit^{commit}") -Quiet
    if ($has.Code -ne 0) { Fail "검토한 커밋 $PinnedCommit 을 찾을 수 없습니다. 설치를 멈춥니다." 'pinned commit not found' }
}
$r = Invoke-Native $git @('-C', $InstallDir, '-c', 'advice.detachedHead=false', 'checkout', '--detach', '--quiet', $PinnedCommit)
$head = (Invoke-Native $git @('-C', $InstallDir, 'rev-parse', 'HEAD') -Quiet).Output.Trim()
if ($r.Code -ne 0 -or $head -ne $PinnedCommit) {
    Fail "커밋 고정에 실패했습니다 (HEAD=$head)." 'could not check out the pinned commit'
}
Ok "HEAD = $head"

# ---------------------------------------------------------------------------
# 4. Aseprite + .env
# ---------------------------------------------------------------------------
Step '4/6 Aseprite.exe 찾기 + .env 작성' 'find Aseprite.exe and write .env'
if ($AsepritePath) {
    if (Test-Path -LiteralPath $AsepritePath -PathType Container) { $AsepritePath = Join-Path $AsepritePath 'Aseprite.exe' }
    if (-not (Test-Path -LiteralPath $AsepritePath -PathType Leaf)) {
        Fail "-AsepritePath 에 파일이 없습니다: $AsepritePath" 'Aseprite.exe not found at -AsepritePath'
    }
    $ase = (Resolve-Path -LiteralPath $AsepritePath).ProviderPath
} else {
    $cands = Find-Aseprite
    if ($cands.Count -eq 0) {
        Fail ('Aseprite.exe 를 찾지 못했습니다. 경로를 직접 알려 주세요. 예:' +
              "`n    powershell -ExecutionPolicy Bypass -File .\tools\aseprite-mcp\setup_windows.ps1 -AsepritePath `"D:\SteamLibrary\steamapps\common\Aseprite\Aseprite.exe`"" +
              "`n    (Steam: 라이브러리에서 Aseprite 우클릭 > 관리 > 로컬 파일 보기)") 'Aseprite.exe not found; pass -AsepritePath'
    }
    $ase = $cands[0]
    if ($cands.Count -gt 1) {
        Say '여러 개를 찾았습니다. 첫 번째를 씁니다 (다른 것을 쓰려면 -AsepritePath):' 'several found; using the first'
        foreach ($c in $cands) { Say "  - $c" '' }
    }
}
Ok "Aseprite: $ase"
if ($ase -match '[^\x00-\x7F]') {
    Warn '경로에 한글 등 ASCII 가 아닌 글자가 있습니다. 문제가 생기면 영문 경로로 옮기세요.' 'non-ASCII characters in the Aseprite path'
}
if (($InstallDir + $env:TEMP) -match '[^\x00-\x7F]') {
    Warn ('설치 폴더나 임시 폴더(%TEMP%) 경로에 한글 등 ASCII 가 아닌 글자가 있습니다 (예: 한글 사용자 이름).' +
          "`n    PYTHONUTF8=1 로 대부분 괜찮지만, 문제가 생기면 -InstallDir C:\tools\aseprite-mcp 처럼 영문 경로로 다시 설치하세요.") 'non-ASCII characters in the install or TEMP path'
}

# python-dotenv decodes \t \n ... inside double quotes. Inside single quotes it only decodes \\ and \',
# so a normal C:\... path is kept as it is. A UNC path (\\server\...) or a path with ' is written with
# forward slashes, and ' is escaped as \'.
$aseForEnv = $ase
if ($aseForEnv.StartsWith('\\') -or $aseForEnv.Contains("'")) {
    $aseForEnv = ($aseForEnv -replace '\\', '/').Replace("'", "\'")
}
$envText = "# Written by pixel-management tools/aseprite-mcp/setup_windows.ps1 - no secrets here.`n" +
           "# The MCP config 'env' (PYTHONUTF8, ASEPRITE_PATH) takes precedence over this file.`n" +
           "ASEPRITE_PATH='$aseForEnv'`n" +
           "ASEPRITE_TIMEOUT_SECONDS=$TimeoutSeconds`n"
$envPath = Join-Path $InstallDir '.env'
if ((Test-Path -LiteralPath $envPath) -and ([System.IO.File]::ReadAllText($envPath) -cne $envText)) { Backup-File $envPath }
Write-Utf8NoBom $envPath $envText
Ok ".env: $envPath"

# ---------------------------------------------------------------------------
# 5. uv sync + self-test
# ---------------------------------------------------------------------------
Step '5/6 uv sync + 자체 시험' 'install locked dependencies and self-test'
Say '처음에는 Python 3.13 과 패키지를 받느라 1~2분 걸릴 수 있습니다.' 'first run downloads Python 3.13 and packages'
$r = Invoke-Native $uv @('sync', '--directory', $InstallDir, '--frozen', '--no-dev')
if ($r.Code -ne 0) { Fail 'uv sync 에 실패했습니다. 위의 메시지를 확인하세요.' 'uv sync failed' }
Ok 'uv sync'

# Import test: loads the package and its tools (registers the tools; core.commands reads .env) but starts
# no server and calls no tool. aseprite_mcp/__init__.py alone imports neither the tools nor core.commands
# (__main__.py does "from .tools import *"), so aseprite_mcp.tools must be imported explicitly.
$savedPath = $env:ASEPRITE_PATH
Remove-Item Env:\ASEPRITE_PATH -ErrorAction SilentlyContinue
$env:PYTHONUTF8 = '1'
$py = "import os, aseprite_mcp as m, aseprite_mcp.tools; names=[t.name for t in m.mcp._tool_manager.list_tools()]; " +
      "deny=['run_lua_script','audit_animation','animation_sanitize','start_preview_server','stop_preview_server']; " +
      "print('IMPORT_OK tools=%d deny_found=%d' % (len(names), sum(d in names for d in deny))); " +
      "print('ENV_PATH=' + str(os.getenv('ASEPRITE_PATH')))"
$r = Invoke-Native $uv @('run', '--directory', $InstallDir, '--frozen', '--no-dev', 'python', '-c', $py) -Quiet
if ($savedPath) { $env:ASEPRITE_PATH = $savedPath }
if ($r.Code -ne 0 -or $r.Output -notmatch 'IMPORT_OK') {
    Write-Host $r.Output
    Fail 'Python 에서 aseprite_mcp 를 불러오지 못했습니다.' 'import test failed'
}
$importLine = ($r.Output -split "`n" | Where-Object { $_ -match 'IMPORT_OK' } | Select-Object -First 1)
$envLine = ($r.Output -split "`n" | Where-Object { $_ -match '^ENV_PATH=' } | Select-Object -First 1)
Ok "import: $importLine"
if ($importLine -notmatch 'deny_found=5') {
    Warn '막을 도구 5개 중 일부가 이 버전에 없습니다. 도구 이름이 바뀌었는지 확인하세요.' 'some denied tool names were not found'
}
$envSeen = ''
if ($envLine) { $envSeen = $envLine.Substring(9).Trim() }
if (($envSeen -replace '/', '\') -ne $ase) {
    Warn ".env 의 ASEPRITE_PATH 가 예상과 다르게 읽혔습니다: '$envSeen' (MCP 설정의 env 값이 우선이라 동작에는 지장 없음)" '.env path read back differently'
} else {
    Ok '.env 의 ASEPRITE_PATH 를 서버가 그대로 읽습니다'
}

$ver = Test-AsepriteVersion $ase
if (-not $ver) {
    Warn ('Aseprite 가 --batch --version 에 응답하지 않았습니다 (60초 안에 끝나지 않았거나 출력 없음).' +
          "`n    Steam 판이 Steam 을 거쳐 다시 실행되면 출력이 사라집니다. Steam 을 켜 둔 채 다시 시험하거나, 같은 폴더의 다른 Aseprite.exe 를 -AsepritePath 로 주세요.") 'Aseprite printed nothing for --batch --version'
} else {
    Ok "Aseprite --batch --version: $ver"
}

# ---------------------------------------------------------------------------
# 6. Register with Claude
# ---------------------------------------------------------------------------
Step '6/6 Claude 에 등록' 'register with Claude'
$serverArgs = @('--directory', $InstallDir, 'run', '--frozen', '--no-dev', '-m', 'aseprite_mcp')
$serverEnv = [ordered]@{ PYTHONUTF8 = '1'; ASEPRITE_PATH = $ase; ASEPRITE_TIMEOUT_SECONDS = "$TimeoutSeconds" }

if (-not $SkipClaudeCode) {
    # 6a. deny rules in the user's Claude Code settings
    $settingsPath = Join-Path $ClaudeConfigDir 'settings.json'
    $settings = Read-JsonFile $settingsPath
    if ($null -eq $settings) {
        Say "아래 줄을 $settingsPath 의 permissions.deny 에 직접 넣으세요:" 'add these to permissions.deny by hand'
        foreach ($t in $DenyTools) { Say "  `"$t`"," '' }
    } else {
        $perm = Get-OrAddObject $settings 'permissions'
        $changed = $false
        $deny = @()
        if ($perm.PSObject.Properties['deny'] -and $null -ne $perm.deny) { $deny = @($perm.deny) }
        foreach ($t in $DenyTools) { if ($deny -notcontains $t) { $deny += $t; $changed = $true } }
        $perm | Add-Member -NotePropertyName deny -NotePropertyValue $deny -Force
        if ($AllowReadOnly) {
            $allow = @()
            if ($perm.PSObject.Properties['allow'] -and $null -ne $perm.allow) { $allow = @($perm.allow) }
            foreach ($t in $ReadOnlyTools) { if ($allow -notcontains $t) { $allow += $t; $changed = $true } }
            $perm | Add-Member -NotePropertyName allow -NotePropertyValue $allow -Force
        }
        if ($changed) {
            Backup-File $settingsPath
            Write-Utf8NoBom $settingsPath ($settings | ConvertTo-Json -Depth 64)
            Ok "deny 규칙 $($DenyTools.Count)개를 넣었습니다: $settingsPath"
        } else {
            Ok "deny 규칙이 이미 들어 있습니다: $settingsPath"
        }
        if ($AllowReadOnly) { Ok "읽기 전용 도구 $($ReadOnlyTools.Count)개 allow" }
    }

    # 6b. claude mcp add --scope user
    $claude = Find-Claude
    $envArgs = @()
    foreach ($k in $serverEnv.Keys) { $envArgs += @('-e', "$k=$($serverEnv[$k])") }
    $addOk = $false
    if ($claude) {
        Invoke-Native $claude @('mcp', 'remove', $ServerName, '--scope', 'user') -Quiet | Out-Null
        $addArgs = @('mcp', 'add', $ServerName, '--scope', 'user') + $envArgs + @('--', $uv) + $serverArgs
        $r = Invoke-Native $claude $addArgs
        $addOk = ($r.Code -eq 0)
        if (-not $addOk) {
            Warn 'claude mcp add 가 실패했습니다. 아래 명령을 직접 실행해 보세요.' 'claude mcp add failed'
        } else {
            Ok 'Claude Code 에 등록했습니다 (user 범위: 모든 폴더에서 쓰임)'
        }
    } else {
        Warn 'claude 명령을 찾지 못했습니다. Claude Code 를 설치했다면 새 PowerShell 에서 아래 명령을 실행하세요.' 'claude not on PATH'
    }
    if (-not $addOk) {
        Say 'npm 으로 설치한 claude 라면 PowerShell 에서는 claude 대신 claude.cmd 로 실행하세요 (claude.ps1 은 -- 를 지웁니다).' 'with an npm install, run it as claude.cmd: PowerShell drops "--" for claude.ps1'
        $q = { param($s) if ($s -match '\s') { "`"$s`"" } else { $s } }
        $line = 'claude mcp add aseprite --scope user'
        foreach ($k in $serverEnv.Keys) { $line += ' -e ' + (& $q "$k=$($serverEnv[$k])") }
        $line += ' -- ' + (& $q $uv)
        foreach ($a in $serverArgs) { $line += ' ' + (& $q $a) }
        Write-Host "    $line" -ForegroundColor White
    }
}

if ($Desktop) {
    $entry = [pscustomobject]@{
        command = $uv
        args    = $serverArgs
        env     = [pscustomobject]$serverEnv
    }
    foreach ($cfgPath in (Get-DesktopConfigPaths)) {
        $cfg = Read-JsonFile $cfgPath
        if ($null -eq $cfg) { continue }
        $servers = Get-OrAddObject $cfg 'mcpServers'
        Backup-File $cfgPath
        $servers | Add-Member -NotePropertyName $ServerName -NotePropertyValue $entry -Force
        Write-Utf8NoBom $cfgPath ($cfg | ConvertTo-Json -Depth 64)
        Ok "Claude Desktop 설정에 넣었습니다: $cfgPath"
    }
    Warn ('Claude Desktop 채팅은 settings.json 의 deny 규칙을 읽지 않습니다. 앱의 aseprite 도구 목록에서 ' +
          'run_lua_script, audit_animation, animation_sanitize, start_preview_server, stop_preview_server 를 꺼 두세요.') 'turn the 5 risky tools off in the Desktop app'
}

Write-Host ''
$exitCode = 0
if (-not $SkipClaudeCode -and -not $addOk) {
    Warn '설치는 끝났지만 Claude Code 등록은 위의 claude mcp add 줄을 직접 실행해야 합니다.' 'installed, but Claude Code registration still has to be run by hand (exit code 2)'
    $exitCode = 2
} else {
    Write-Host '완료 / Done' -ForegroundColor Green
}
Say 'Claude 앱(또는 claude 세션)을 완전히 끄고 다시 켜세요. 그 뒤 /mcp 로 aseprite 가 connected 인지 확인합니다.' 'restart Claude, then check /mcp'
Say '확인용 요청 예: "aseprite 도구로 get_sprite_info 를 이 파일에 실행해 줘: <절대 경로>.aseprite"' 'smoke test with get_sprite_info'
exit $exitCode
