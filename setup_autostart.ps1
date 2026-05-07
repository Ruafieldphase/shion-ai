$ws = New-Object -ComObject WScript.Shell
$startupPath = $ws.SpecialFolders("Startup")

# 이전 Registry Run 엔트리 제거. 이것이 남아 있으면 heart/Ollama를 건너뛰고
# orchestrator만 pythonw로 떠서 재부팅 후 반쯤 깨어 있는 상태가 됩니다.
$runPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
if (Get-ItemProperty -Path $runPath -Name "ShionOrchestrator" -ErrorAction SilentlyContinue) {
    Remove-ItemProperty -Path $runPath -Name "ShionOrchestrator" -ErrorAction SilentlyContinue
    Write-Host "Removed old HKCU Run entry: ShionOrchestrator"
}

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
$shortcut.Arguments = "auto-visible"
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.WindowStyle = 1  # Normal visible window
$shortcut.Save()

Write-Host "Created: $shortcutPath"
Write-Host "On login: Ollama -> Heart -> Pulse (single visible automatic stack)"
