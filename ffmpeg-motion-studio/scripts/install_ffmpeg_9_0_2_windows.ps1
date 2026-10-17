[CmdletBinding()]
param(
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA 'FFmpeg-MotionStudio\9.0.2'),
    [switch]$AddToUserPath,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Version = '9.0.2'
$PackageUrl = 'https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-9.0.2-essentials_build.zip'
$ExpectedSha256 = '60f467265b1e312373dbcd92200c2618a74850f98d3d078e94296bb3fa2047ba'
if ([string]::IsNullOrWhiteSpace($InstallRoot)) { throw 'InstallRoot cannot be empty.' }
$Target = [System.IO.Path]::GetFullPath($InstallRoot)
$Parent = Split-Path -Parent $Target
if ([string]::IsNullOrWhiteSpace($Parent) -or $Target -eq [System.IO.Path]::GetPathRoot($Target)) { throw "Unsafe install destination: $Target" }
if ((Test-Path $Target) -and -not $Force) { throw "Target exists: $Target. Use -Force to replace it; the old directory will be backed up, not deleted." }

$Work = Join-Path $env:TEMP ("ffmpeg-motion-studio-9.0.2-" + [Guid]::NewGuid().ToString('N'))
$Archive = Join-Path $Work 'ffmpeg-9.0.2-essentials_build.zip'
$Extract = Join-Path $Work 'extract'
$Stage = "$Target.stage.$PID"
$Backup = $null
try {
    New-Item -ItemType Directory -Path $Work -Force | Out-Null
    New-Item -ItemType Directory -Path $Extract -Force | Out-Null
    New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    Write-Host "Downloading pinned FFmpeg $Version Windows build..."
    Invoke-WebRequest -Uri $PackageUrl -OutFile $Archive -UseBasicParsing
    $ActualSha256 = (Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($ActualSha256 -ne $ExpectedSha256) { throw "SHA-256 mismatch. Expected $ExpectedSha256; got $ActualSha256. Refusing to install." }

    Expand-Archive -LiteralPath $Archive -DestinationPath $Extract -Force
    $BuildRoot = Get-ChildItem -LiteralPath $Extract -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'bin\ffmpeg.exe') } | Select-Object -First 1
    if (-not $BuildRoot -and (Test-Path (Join-Path $Extract 'bin\ffmpeg.exe'))) { $BuildRoot = Get-Item -LiteralPath $Extract }
    if (-not $BuildRoot) { throw 'Verified archive lacks bin\ffmpeg.exe.' }
    if (-not (Test-Path (Join-Path $BuildRoot.FullName 'bin\ffprobe.exe'))) { throw 'Verified archive lacks bin\ffprobe.exe.' }
    if (Test-Path $Stage) { Remove-Item -LiteralPath $Stage -Recurse -Force }
    New-Item -ItemType Directory -Path $Stage -Force | Out-Null
    Get-ChildItem -LiteralPath $BuildRoot.FullName -Force | Copy-Item -Destination $Stage -Recurse -Force

    $Ffmpeg = Join-Path $Stage 'bin\ffmpeg.exe'
    $Ffprobe = Join-Path $Stage 'bin\ffprobe.exe'
    $VersionOutput = (& $Ffmpeg -hide_banner -version 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0 -or $VersionOutput -notmatch 'ffmpeg version 9\.0\.2') { throw "FFmpeg version assertion failed: $VersionOutput" }
    $FfprobeVersion = (& $Ffprobe -hide_banner -version 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0 -or $FfprobeVersion -notmatch 'ffprobe version 9\.0\.2') { throw "FFprobe version assertion failed: $FfprobeVersion" }

    $EncoderText = (& $Ffmpeg -hide_banner -encoders 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) { throw 'Could not enumerate encoders.' }
    foreach ($Encoder in @('libx264', 'libx265', 'libvpx-vp9', 'libaom-av1')) {
        if ($EncoderText -notmatch ("\b" + [regex]::Escape($Encoder) + "\b")) { throw "Required encoder missing: $Encoder" }
    }
    $FilterText = (& $Ffmpeg -hide_banner -filters 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) { throw 'Could not enumerate filters.' }
    foreach ($Filter in @('drawtext', 'subtitles', 'loudnorm', 'xfade', 'acrossfade', 'zscale')) {
        if ($FilterText -notmatch ("\b" + [regex]::Escape($Filter) + "\b")) { throw "Required filter missing: $Filter" }
    }

    $SmokeFile = Join-Path $Work 'smoke-av.mp4'
    $EncodeArgs = @('-hide_banner','-loglevel','error','-y','-f','lavfi','-i','testsrc2=size=320x180:rate=24:duration=2','-f','lavfi','-i','sine=frequency=997:sample_rate=48000:duration=2','-c:v','libx264','-preset','ultrafast','-crf','28','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-shortest',$SmokeFile)
    & $Ffmpeg @EncodeArgs
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $SmokeFile)) { throw 'H.264/AAC smoke encode failed.' }
    $ProbeText = (& $Ffprobe -v error -show_streams -show_format -of json $SmokeFile | Out-String)
    if ($LASTEXITCODE -ne 0) { throw 'FFprobe failed to inspect smoke output.' }
    $Probe = $ProbeText | ConvertFrom-Json
    $Video = $Probe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1
    $Audio = $Probe.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1
    if (-not $Video -or -not $Audio) { throw 'Smoke output must contain video and audio streams.' }
    if ([int]$Video.width -ne 320 -or [int]$Video.height -ne 180) { throw 'Smoke resolution mismatch.' }
    if ([string]$Video.r_frame_rate -ne '24/1') { throw "Smoke frame-rate mismatch: $($Video.r_frame_rate)" }
    if ([string]$Video.codec_name -ne 'h264' -or [string]$Audio.codec_name -ne 'aac') { throw 'Smoke codec mismatch.' }
    $Duration = [double]::Parse([string]$Probe.format.duration, [Globalization.CultureInfo]::InvariantCulture)
    if ($Duration -lt 1.90 -or $Duration -gt 2.20) { throw "Smoke duration mismatch: $Duration" }

    $Report = [ordered]@{
        version = $Version
        platform = 'Windows x86_64'
        package_url = $PackageUrl
        package_sha256_expected = $ExpectedSha256
        package_sha256_actual = $ActualSha256
        ffmpeg_first_line = (($VersionOutput.Split([Environment]::NewLine) | Select-Object -First 1).Trim())
        ffprobe_first_line = (($FfprobeVersion.Split([Environment]::NewLine) | Select-Object -First 1).Trim())
        install_path = $Target
        checks = [ordered]@{ package_sha256 = $true; ffmpeg_version = $true; ffprobe_version = $true; required_encoders = $true; required_filters = $true; h264_aac_encode_and_mux = $true; ffprobe_stream_resolution_and_fps = $true; media_duration_seconds = [Math]::Round($Duration, 3) }
        smoke_output_sha256 = (Get-FileHash -LiteralPath $SmokeFile -Algorithm SHA256).Hash.ToLowerInvariant()
        validated_at_utc = [DateTime]::UtcNow.ToString('o')
        note = 'Pinned upstream Gyan Windows build verified and tested; system-wide FFmpeg is not replaced.'
    }
    $Report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Stage 'ffmpeg-upgrade-report.json') -Encoding UTF8

    if (Test-Path $Target) {
        $Backup = "$Target.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Move-Item -LiteralPath $Target -Destination $Backup
    }
    try { Move-Item -LiteralPath $Stage -Destination $Target }
    catch {
        if ($Backup -and (Test-Path $Backup) -and -not (Test-Path $Target)) { Move-Item -LiteralPath $Backup -Destination $Target }
        throw
    }

    $Ffmpeg = Join-Path $Target 'bin\ffmpeg.exe'
    $Ffprobe = Join-Path $Target 'bin\ffprobe.exe'
    if ($AddToUserPath) {
        $BinPath = Join-Path $Target 'bin'
        $UserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
        $UserEntries = @($UserPath -split ';' | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
        if (-not ($UserEntries | Where-Object { $_.TrimEnd('\') -ieq $BinPath.TrimEnd('\') })) { [Environment]::SetEnvironmentVariable('Path', (@($BinPath) + $UserEntries -join ';'), 'User') }
        $env:Path = "$BinPath;$env:Path"
        Write-Warning 'User PATH updated; a machine-level entry may still take precedence in new shells. Verify using Get-Command ffmpeg -All.'
    }
    Write-Host ([Environment]::NewLine + "Installed and validated FFmpeg $Version at: $Target")
    Write-Host "FFmpeg:  $Ffmpeg"
    Write-Host "FFprobe: $Ffprobe"
    Write-Host "Report:  $(Join-Path $Target 'ffmpeg-upgrade-report.json')"
    if ($Backup) { Write-Host "Previous target preserved at: $Backup" }
}
finally {
    if (Test-Path $Stage) { Remove-Item -LiteralPath $Stage -Recurse -Force -ErrorAction SilentlyContinue }
    if (Test-Path $Work) { Remove-Item -LiteralPath $Work -Recurse -Force -ErrorAction SilentlyContinue }
}
