$ErrorActionPreference = 'Stop'
$PackageName = 'com.noodlecake.drtc'
$CaptureSeconds = 90

function Fail([string]$Message) {
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

Write-Host '=== DR2C VORENYX Install/Start Runtime Trace v2.65 ==='
Write-Host '[1] Rekam percobaan instalasi yang gagal (aplikasi boleh belum terpasang)'
Write-Host '[2] Rekam aplikasi terpasang saat tombol Start tidak merespons'
$modeChoice = Read-Host 'Pilih mode 1 atau 2'
if ($modeChoice -notin @('1','2')) { Fail 'Pilihan mode harus 1 atau 2.' }
$traceMode = if ($modeChoice -eq '1') { 'INSTALL_ATTEMPT' } else { 'START_BUTTON' }

$adbCommand = Get-Command adb -ErrorAction SilentlyContinue
if (-not $adbCommand) {
    Fail 'adb tidak ditemukan. Install Android Platform Tools, lalu pastikan adb.exe ada di PATH.'
}
$adbPath = $adbCommand.Source
Write-Host 'Perangkat harus mengaktifkan USB debugging dan menyetujui dialog otorisasi.'
$deviceOutput = & $adbPath devices
$deviceRows = @($deviceOutput | Select-Object -Skip 1 | Where-Object { $_ -match '^\S+\s+device(\s|$)' })
if ($deviceRows.Count -eq 0) {
    Write-Host ($deviceOutput -join [Environment]::NewLine)
    Fail 'Tidak ada perangkat berstatus device. Periksa kabel, USB debugging, atau otorisasi.'
}
$serials = @($deviceRows | ForEach-Object { ($_ -split '\s+')[0] })
if ($serials.Count -eq 1) {
    $serial = $serials[0]
} else {
    Write-Host 'Perangkat aktif:'
    for ($i = 0; $i -lt $serials.Count; $i++) { Write-Host "[$i] $($serials[$i])" }
    $pick = Read-Host 'Pilih indeks perangkat'
    if ($pick -notmatch '^\d+$' -or [int]$pick -ge $serials.Count) { Fail 'Pilihan perangkat tidak valid.' }
    $serial = $serials[[int]$pick]
}

$installedBefore = $false
$pathBefore = & $adbPath -s $serial shell pm path $PackageName 2>$null
if ($pathBefore -and ($pathBefore -join '') -match 'package:') { $installedBefore = $true }
if ($traceMode -eq 'START_BUTTON' -and -not $installedBefore) {
    Fail "Paket $PackageName tidak terdeteksi. Jalankan mode 1 untuk merekam percobaan instalasi; skrip tidak memasang apa pun otomatis."
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$desktop = [Environment]::GetFolderPath('Desktop')
if (-not $desktop -or -not (Test-Path $desktop)) { $desktop = (Get-Location).Path }
$outDir = Join-Path $desktop "DR2C-Trace-$stamp"
New-Item -ItemType Directory -Path $outDir | Out-Null
$rawLog = Join-Path $outDir 'logcat-raw-temporary.txt'
$logErr = Join-Path $outDir 'logcat-stderr-temporary.txt'
$filteredLog = Join-Path $outDir 'logcat-relevant-lines.txt'
$packageInfo = Join-Path $outDir 'package-info-before-after.txt'
$activityInfo = Join-Path $outDir 'activity-package-lines.txt'
$metaInfo = Join-Path $outDir 'capture-info.txt'
$logProcess = $null

function Write-PackageSnapshot([string]$Label) {
    Add-Content -Encoding UTF8 $packageInfo "--- $Label ---"
    $dump = & $adbPath -s $serial shell dumpsys package $PackageName 2>&1
    $selected = @($dump | Where-Object { $_ -match 'Unable to find package|Package \[|versionCode=|versionName=|minSdk=|targetSdk=|codePath=|primaryCpuAbi=|secondaryCpuAbi=|signatures=|SigningInfo|installerPackageName=|firstInstallTime=|lastUpdateTime=' })
    if ($selected.Count -eq 0) { $selected = @('(No matching package metadata returned)') }
    $selected | Add-Content -Encoding UTF8 $packageInfo
}

try {
    @(
        "Capture date (local): $(Get-Date -Format o)"
        "Trace mode: $traceMode"
        "Package: $PackageName"
        "Android device serial: (not stored)"
        "Installed before capture: $installedBefore"
        "Capture window: up to $CaptureSeconds seconds; ends automatically"
        'Purpose: classify install/launch/runtime failures; this is not a license bypass.'
    ) | Set-Content -Encoding UTF8 $metaInfo
    $sdk = & $adbPath -s $serial shell getprop ro.build.version.release 2>$null
    $sdkInt = & $adbPath -s $serial shell getprop ro.build.version.sdk 2>$null
    Add-Content -Encoding UTF8 $metaInfo "Android release: $($sdk -join '')"
    Add-Content -Encoding UTF8 $metaInfo "Android SDK: $($sdkInt -join '')"
    Write-PackageSnapshot 'BEFORE CAPTURE'

    # Never clear device-wide logs. Start at the recent/live edge instead.
    $logArgs = @('-s', $serial, 'logcat', '-b', 'all', '-v', 'threadtime', '-T', '1')
    $logProcess = Start-Process -FilePath $adbPath -ArgumentList $logArgs -PassThru -RedirectStandardOutput $rawLog -RedirectStandardError $logErr -WindowStyle Hidden
    Start-Sleep -Milliseconds 700
    if ($logProcess.HasExited) {
        $errText = if (Test-Path $logErr) { (Get-Content $logErr -Raw -ErrorAction SilentlyContinue) } else { '' }
        Fail "Logcat process exited before capture. $errText"
    }

    Write-Host ''
    Write-Host 'CAPTURE AKTIF.' -ForegroundColor Green
    if ($traceMode -eq 'INSTALL_ATTEMPT') {
        Write-Host "Dalam $CaptureSeconds detik, coba pasang APK melalui cara biasa di ponsel. Jangan uninstall aplikasi lain atau menghapus data."
        Write-Host 'Jika muncul pesan gagal memasang, tunggu sekitar 10 detik lalu biarkan perekaman berakhir otomatis.'
    } else {
        Write-Host "Dalam $CaptureSeconds detik, buka DR2C VORENYX, tekan Start SATU KALI, lalu tunggu sekitar 10 detik."
        Write-Host 'Jangan uninstall/reinstall aplikasi saat sesi ini.'
    }
    Write-Host 'Biarkan jendela ini terbuka; perekaman berhenti otomatis.'
    $finished = $logProcess.WaitForExit($CaptureSeconds * 1000)
    if (-not $finished -and -not $logProcess.HasExited) {
        Stop-Process -Id $logProcess.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
} catch {
    Write-Host "Capture berhenti: $($_.Exception.Message)" -ForegroundColor Yellow
} finally {
    if ($logProcess -and -not $logProcess.HasExited) {
        Stop-Process -Id $logProcess.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
}

if (Test-Path $rawLog) {
    if ($traceMode -eq 'INSTALL_ATTEMPT') {
        $pattern = 'com\.noodlecake\.drtc|PackageInstaller|PackageManager|PackageManagerService|installd|INSTALL_FAILED|INSTALL_PARSE_FAILED|Failure \[|INSTALL_FAILED_UPDATE_INCOMPATIBLE|INSTALL_FAILED_NO_MATCHING_ABIS|INSTALL_FAILED_OLDER_SDK|INSTALL_FAILED_DEXOPT|signature|Verification|parse error|parse failed|Could not install|Failed to install|not installed|INSTALL_FAILED_BAD_SIGNATURE|INSTALL_FAILED_INVALID_APK|INSTALL_FAILED_MISSING_SHARED_LIBRARY|INSTALL_FAILED_SHARED_USER_INCOMPATIBLE'
    } else {
        $pattern = 'com\.noodlecake\.drtc|AndroidRuntime|FATAL EXCEPTION|Fatal signal|SIGSEGV|SIGABRT|UnsatisfiedLinkError|VerifyError|ClassNotFoundException|NoClassDefFoundError|PairIP|pairip|Deathforth|deathforth|DRTC|drtc|ANR in|am_crash|am_anr|native_crash|JNI DETECTED ERROR|integrity|signature|license|licence|Unable to load|could not find|couldn''t find|dlopen failed'
    }
    Select-String -Path $rawLog -Pattern $pattern -CaseSensitive:$false | ForEach-Object { $_.Line } | Set-Content -Encoding UTF8 $filteredLog
    Remove-Item $rawLog -Force -ErrorAction SilentlyContinue
}
if (Test-Path $logErr) { Remove-Item $logErr -Force -ErrorAction SilentlyContinue }

$pathAfter = & $adbPath -s $serial shell pm path $PackageName 2>$null
$installedAfter = [bool]($pathAfter -and ($pathAfter -join '') -match 'package:')
Add-Content -Encoding UTF8 $metaInfo "Installed after capture: $installedAfter"
Write-PackageSnapshot 'AFTER CAPTURE'
$actDump = & $adbPath -s $serial shell dumpsys activity activities 2>$null
$actDump | Where-Object { $_ -match 'com\.noodlecake\.drtc|mResumedActivity|topResumedActivity|Resumed:' } | Set-Content -Encoding UTF8 $activityInfo

$zipPath = Join-Path $desktop "DR2C-Trace-$stamp.zip"
Compress-Archive -Path (Join-Path $outDir '*') -DestinationPath $zipPath -Force
Write-Host ''
Write-Host 'Selesai. Paket trace sudah dibuat:' -ForegroundColor Green
Write-Host $zipPath
Write-Host 'Periksa ZIP sebelum membagikan; log mentah dan stderr tidak disertakan.'
Write-Host 'Collector tidak memasang APK secara otomatis, tidak menghapus log Android, tidak menyentuh save, dan tidak mem-bypass lisensi/signature.'
