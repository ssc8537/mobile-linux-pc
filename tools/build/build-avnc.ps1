# Build the patched AVNC AAR (Kotlin + resources only; the native .so comes from jniLibs)
# and publish it into the local maven repository that tiny_container consumes.
#
# Usage:
#   cd <root>
#   iex (Get-Content "tools\build\build-avnc.ps1" -Raw -Encoding UTF8)
#
# Requires Gradle 8.13 (NOT 9.x): the AVNC module uses AGP 8.10.1, which 9.x refuses.
# Requires the prebuilt native libs to already be in app/src/main/jniLibs/<abi>/ — see
# tools/patch/extract_aar_jni.py.
#
# Override these with env vars before running:
#   $env:AVNC_DIR         path to the avnc checkout
#   $env:AVNC_MAVEN_LOCAL where to publish (must match what settings.gradle.kts resolves)
$ErrorActionPreference = 'Continue'

$Work = (Get-Location).Path

function Resolve-AvncDir {
    param([string]$Root, [string]$Preferred)
    if ($Preferred -and (Test-Path (Join-Path $Preferred 'gradlew'))) { return $Preferred }
    foreach ($c in @((Join-Path $Root 'avnc-upstream-fork-deletable'), (Join-Path $Root 'source\avnc'))) {
        if (Test-Path (Join-Path $c 'gradlew')) { return $c }
    }
    return $null
}

$Avnc = Resolve-AvncDir -Root $Work -Preferred $env:AVNC_DIR
if (-not $Avnc) {
    "ERROR: could not find the avnc project (no gradlew found) under $Work"
    "GRADLE_EXIT=1"
    return
}
"AVNC_PROJECT=$Avnc"

if (-not (Test-Path (Join-Path $Avnc 'app\src\main\jniLibs\arm64-v8a\libnative-vnc.so'))) {
    "WARNING: app/src/main/jniLibs/<abi>/libnative-vnc.so is missing."
    "Extract it first:  python tools\patch\extract_aar_jni.py <avnc.aar> $Avnc\app\src\main\jniLibs"
    "Otherwise the AAR will build but ship without the native VNC engine."
}

$Tool = Join-Path $Work 'build-env-toolchain'
if (Test-Path $Tool) {
    $env:JAVA_HOME          = Join-Path $Tool 'jdk21-runtime-deletable\jdk-21.0.13+9'
    $env:ANDROID_HOME       = Join-Path $Tool 'sdk-android-platform-tools-deletable'
    $env:ANDROID_SDK_ROOT   = $env:ANDROID_HOME
    $env:ANDROID_USER_HOME  = Join-Path $Tool 'gradle-home-cache-deletable\android-user-home'
    $env:GRADLE_USER_HOME   = Join-Path $Tool 'gradle-home-cache-deletable'
    $env:GRADLE_OPTS        = '-Dfile.encoding=UTF-8'
    $env:PATH = (Join-Path $env:JAVA_HOME 'bin') + ';' +
                (Join-Path $Tool 'gradle-home-cache-deletable\gradle-dist\gradle-8.13\bin') + ';' +
                (Join-Path $env:ANDROID_HOME 'cmdline-tools\latest\bin') + ';' +
                (Join-Path $env:ANDROID_HOME 'platform-tools') + ';' + $env:PATH
    $log = Join-Path $Tool 'log-build-avnc.txt'
} else {
    "NOTE: no build-env-toolchain found, using JDK/SDK/Gradle from PATH (must be Gradle 8.x)."
    $log = Join-Path $Work 'log-build-avnc.txt'
}

# AGP 8.10.1 still resolves some artifacts from the network on a cold cache.
$env:HTTP_PROXY  = 'http://127.0.0.1:7897'
$env:HTTPS_PROXY = 'http://127.0.0.1:7897'
$env:NO_PROXY    = ''

Push-Location $Avnc
& gradle publishReleasePublicationToLocalForkRepository --no-daemon --console=plain 2>&1 | Tee-Object -FilePath $log
$code = $LASTEXITCODE
Pop-Location
"GRADLE_EXIT=$code"
