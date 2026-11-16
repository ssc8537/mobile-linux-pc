# Build the tiny_container release APK from the patched build copy.
# Run from the workspace root with:
#   iex (Get-Content "build-env-toolchain\build-apk.ps1" -Raw -Encoding UTF8)
# NOTE: $PSScriptRoot is EMPTY under `iex`, so paths are derived from $PWD instead.
$ErrorActionPreference = 'Continue'

$Work = (Get-Location).Path
$Tool = Join-Path $Work 'build-env-toolchain'
$Build = Join-Path $Tool 'ws-gradle-build-copy-deletable\tiny_container'

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

# Local maven repo must be reachable through the (offline) gradle cache; no proxy needed.
$env:HTTP_PROXY  = ''
$env:HTTPS_PROXY = ''
$env:NO_PROXY    = '*'

$log = Join-Path $Tool 'log-build-apk.txt'
Push-Location $Build
& gradle assembleRelease --no-daemon --no-watch-fs --console=plain 2>&1 | Tee-Object -FilePath $log
$code = $LASTEXITCODE
Pop-Location
"GRADLE_EXIT=$code"
