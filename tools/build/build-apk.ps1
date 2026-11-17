# Build the tiny_container release APK.
#
# Two supported layouts, auto-detected from the current directory:
#   A) original workspace : <root>/build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container
#   B) plain git clone    : <root>/source/app
#
# Usage:
#   cd <root>
#   iex (Get-Content "tools\build\env.ps1" -Raw -Encoding UTF8)   # optional, sets PATH
#   iex (Get-Content "tools\build\build-apk.ps1" -Raw -Encoding UTF8)
#
# Override the project to build with $env:BUILD_DIR before running.
# NOTE: $PSScriptRoot is EMPTY under `iex`, so paths come from $PWD / env vars.
$ErrorActionPreference = 'Continue'

$Work = (Get-Location).Path

function Resolve-ProjectDir {
    param([string]$Root, [string]$Preferred)
    if ($Preferred -and (Test-Path (Join-Path $Preferred 'gradlew'))) { return $Preferred }
    $candidates = @(
        (Join-Path $Root 'build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container'),
        (Join-Path $Root 'source\app'),
        $Root
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path (Join-Path $c 'gradlew'))) { return $c }
    }
    return $null
}

$Build = Resolve-ProjectDir -Root $Work -Preferred $env:BUILD_DIR
if (-not $Build) {
    "ERROR: could not find the tiny_container project (no gradlew found)."
    "Looked under: $Work"
    "Set `$env:BUILD_DIR to the folder that contains gradlew."
    "GRADLE_EXIT=1"
    return
}
"BUILD_PROJECT=$Build"

# Use the toolchain bundled next to the workspace when it exists; otherwise rely on
# whatever JDK / Android SDK / Gradle are already on PATH.
$Tool = Join-Path $Work 'build-env-toolchain'
if (Test-Path $Tool) {
    $env:JAVA_HOME          = Join-Path $Tool 'jdk21-runtime-deletable\jdk-21.0.13+9'
    $env:ANDROID_HOME       = Join-Path $Tool 'sdk-android-platform-tools-deletable'
    $env:ANDROID_SDK_ROOT   = $env:ANDROID_HOME
    $env:ANDROID_USER_HOME  = Join-Path $Tool 'gradle-home-cache-deletable\android-user-home'
    $env:GRADLE_USER_HOME   = Join-Path $Tool 'gradle-home-cache-deletable'
    $env:GRADLE_OPTS        = '-Dfile.encoding=UTF-8'
    $env:PATH = (Join-Path $env:JAVA_HOME 'bin') + ';' +
                (Join-Path $Tool 'gradle-home-cache-deletable\gradle-dist\gradle-9.4.1\bin') + ';' +
                (Join-Path $env:ANDROID_HOME 'cmdline-tools\latest\bin') + ';' +
                (Join-Path $env:ANDROID_HOME 'platform-tools') + ';' + $env:PATH
    $log = Join-Path $Tool 'log-build-apk.txt'
} else {
    "NOTE: no build-env-toolchain found, using JDK/SDK/Gradle from PATH."
    $log = Join-Path $Work 'log-build-apk.txt'
}

# A local maven repo needs no proxy; keep all traffic off the slow proxy.
$env:HTTP_PROXY  = ''
$env:HTTPS_PROXY = ''
$env:NO_PROXY    = '*'

Push-Location $Build
& gradle assembleRelease --no-daemon --no-watch-fs --console=plain 2>&1 | Tee-Object -FilePath $log
$code = $LASTEXITCODE
Pop-Location
"GRADLE_EXIT=$code"
