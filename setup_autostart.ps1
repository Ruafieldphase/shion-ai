$ws = New-Object -ComObject WScript.Shell
$startupPath = $ws.SpecialFolders("Startup")

# 이전 심장 전용 바로가기 삭제
$oldShortcut = Join-Path $startupPath "ShionV1Heart.lnk"
if (Test-Path $oldShortcut) {
    Remove-Item $oldShortcut
    Write-Host "Removed old heart-only shortcut."
}

# 통합 무의식 바로가기 생성
$shortcutPath = Join-Path $startupPath "ShionUnconscious.lnk"

$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $PSScriptRoot "start_unconscious.bat"
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.WindowStyle = 7  # Minimized
$shortcut.Save()

Write-Host "Created: $shortcutPath"
Write-Host "On login: Heart -> Wait -> Pulse (all automatic)"
