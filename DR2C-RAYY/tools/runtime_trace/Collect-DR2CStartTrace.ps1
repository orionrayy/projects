$ErrorActionPreference = 'Stop'
$PackageName = 'com.noodlecake.drtc'

function Fail([string]$Message) {
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

$adbCommand = Get-Command adb -ErrorAction SilentlyContinue
if (-not $adbCommand) {
    Fail 'adb tidak ditemukan. Install Android Platform Tools, lalu pastikan adb.exe ada di PATH.'
}
$adbPath = $adbCommand.Source

Write-Host '=== DR2C VORENYX Start Trace (read-only; no install/uninstall) ==='
Write-Host 'Perangkat harus mengaktifkan USB debugging dan menyetujui dialog otorisasi.'
$deviceOutput = & $adbPath devices
$deviceRows = @($deviceOutput | Select-Object -Skip 1 | Where-Object { $_ -match '^\S+\s+device(\s|$)' })
if ($deviceRows.Count -eq 0) {
    Write-Host ($deviceOutput -join "`n")
    Fail 'Tidak ada perangkat berstatus device. Periksa kabel/USB debugging/otorisasi.'
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

$pathLine = & $adbPath -s $serial shell pm path $PackageName 2>$null
if (-not $pathLine -or ($pathLine -join '') -notmatch 'package:') {
    Fail "Paket $PackageName tidak terdeteksi pada perangkat yang dipilih. Skrip tidak memasang atau menghapus apa pun."
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$desktop = [Environment]::GetFolderPath('Desktop')
if (-not $desktop -or -not (Test-Path $desktop)) { $desktop = (Get-Location).Path }
$outDir = Join-Path $desktop "DR2C-StartTrace-$stamp"
New-Item -ItemType Directory -Path $outDir | Out-Null
$rawLog = Join-Path $outDir 'logcat-raw-temporary.txt'
$logErr = Join-Path $outDir 'logcat-stderr-temporary.txt'
$filteredLog = Join-Path $outDir 'logcat-relevant-lines.txt'
$packageInfo = Join-Path $outDir 'package-info.txt'
$crashInfo = Join-Path $outDir 'crash-buffer-relevant-lines.txt'
$activityInfo = Join-Path $outDir 'activity-package-lines.txt'
$metaInfo = Join-Path $outDir 'capture-info.txt'
$logProcess = $null

try {
    @(
        "Capture date (local): $(Get-Date -Format o)"
        "Package: $PackageName"
        "Android device serial: (not stored)"
        'Purpose: distinguish launch/touch dispatch/native/runtime errors; this is not a license bypass.'
    ) | Set-Content -Encoding UTF8 $metaInfo

    $pkgDump = & $adbPath -s $serial shell dumpsys package $PackageName 2>&1
    $pkgDump | Where-Object { $_ -match 'Package \[|versionCode=|versionName=|minSdk=|targetSdk=|codePath=|primaryCpuAbi=|secondaryCpuAbi=|signatures=|SigningInfo|installerPackageName=|firstInstallTime=|lastUpdateTime=' } | Set-Content -Encoding UTF8 $packageInfo
    $sdk = & $adbPath -s $serial shell getprop ro.build.version.release 2>$null
    $sdkInt = & $adbPath -s $serial shell getprop ro.build.version.sdk 2>$null
    Add-Content -Encoding UTF8 $metaInfo "Android release: $($sdk -join '')"
    Add-Content -Encoding UTF8 $metaInfo "Android SDK: $($sdkInt -join '')"

    & $adbPath -s $serial logcat -c 2>$null
    if ($LASTEXITCODE -ne 0) { Fail 'Gagal mengosongkan buffer logcat. Periksa izin dan koneksi perangkat.' }

    $logArgs = @('-s', $serial, 'logcat', '-b', 'all', '-v', 'threadtime')
    $logProcess = Start-Process -FilePath $adbPath -ArgumentList $logArgs -PassThru -RedirectStandardOutput $rawLog -RedirectStandardError $logErr -WindowStyle Hidden

    Write-Host ''
    Write-Host 'CAPTURE AKTIF.' -ForegroundColor Green
    Write-Host 'Di ponsel: buka DR2C VORENYX, tekan Start satu kali, tunggu sekitar 10 detik.'
    Write-Host 'Jangan uninstall/reinstall aplikasi saat sesi ini.'
    [void](Read-Host 'Setelah tap Start dan menunggu, tekan ENTER di sini untuk selesai')
} catch {
    Write-Host "Capture berhenti: $($_.Exception.Message)" -ForegroundColor Yellow
} finally {
    if ($logProcess -and -not $logProcess.HasExited) {
        Stop-Process -Id $logProcess.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
}

if (Test-Path $rawLog) {
    $pattern = 'com\.noodlecake\.drtc|AndroidRuntime|FATAL EXCEPTION|Fatal signal|SIGSEGV|SIGABRT|UnsatisfiedLinkError|VerifyError|ClassNotFoundException|NoClassDefFoundError|PairIP|pairip|Deathforth|deathforth|DRTC|drtc|InputDispatcher|InputReader|ActivityTaskManager|ActivityManager|WindowManager|Choreographer|ANR in|am_crash|am_anr|native_crash|libc|linker|JNI DETECTED ERROR|denied|integrity|signature|license|licence|touch|MotionEvent|START'
    Select-String -Path $rawLog -Pattern $pattern -CaseSensitive:$false | ForEach-Object { $_.Line } | Set-Content -Encoding UTF8 $filteredLog
    Remove-Item $rawLog -Force -ErrorAction SilentlyContinue
}
if (Test-Path $logErr) { Remove-Item $logErr -Force -ErrorAction SilentlyContinue }

$crashDump = & $adbPath -s $serial logcat -b crash -d -v threadtime 2>$null
$crashDump | Where-Object { $_ -match 'com\.noodlecake\.drtc|AndroidRuntime|FATAL|Fatal signal|SIGSEGV|SIGABRT|PairIP|Deathforth|drtc|libc|linker|JNI' } | Set-Content -Encoding UTF8 $crashInfo
$actDump = & $adbPath -s $serial shell dumpsys activity activities 2>$null
$actDump | Where-Object { $_ -match 'com\.noodlecake\.drtc|mResumedActivity|topResumedActivity|Resumed:' } | Set-Content -Encoding UTF8 $activityInfo

$zipPath = Join-Path $desktop "DR2C-StartTrace-$stamp.zip"
Compress-Archive -Path (Join-Path $outDir '*') -DestinationPath $zipPath -Force
Write-Host ''
Write-Host 'Selesai. Paket trace sudah dibuat:' -ForegroundColor Green
Write-Host $zipPath
Write-Host 'Periksa isi ZIP sebelum membagikannya. Log sistem yang tidak relevan sengaja difilter, dan log mentah tidak dimasukkan.'
Write-Host 'Skrip ini hanya membaca status paket/log; tidak mengubah APK, signature, save, atau lisensi.'
