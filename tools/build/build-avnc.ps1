# Build the patched AVNC AAR (Kotlin only; native .so comes from jniLibs).
# Run from the workspace root with:
#   iex (Get-Content "build-env-toolchain\build-avnc.ps1" -Raw -Encoding UTF8)
# NOTE: $PSScriptRoot is EMPTY under `iex`, so paths are derived from $PWD instead.
$ErrorActionPreference = 'Continue'

$Work = (Get-Location).Path
$Tool = Join-Path $Work 'build-env-toolchain'
$Avnc = Join-Path $Work 'avnc-upstream-fork-deletable'

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

$env:HTTP_PROXY  = 'http://127.0.0.1:7897'
$env:HTTPS_PROXY = 'http://127.0.0.1:7897'
$env:NO_PROXY    = ''

$log = Join-Path $Tool 'log-build-avnc.txt'
Push-Location $Avnc
& gradle publishReleasePublicationToLocalForkRepository --no-daemon --console=plain 2>&1 | Tee-Object -FilePath $log
$code = $LASTEXITCODE
Pop-Location
"GRADLE_EXIT=$code"
