# env.ps1 -- build environment initialisation for this session (deletable)
$ErrorActionPreference = 'Continue'
$Root = 'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
$Tool = Join-Path $Root 'build-env-toolchain'

$env:JAVA_HOME         = Join-Path $Tool 'jdk21-runtime-deletable\jdk-21.0.13+9'
$env:ANDROID_HOME      = Join-Path $Tool 'sdk-android-platform-tools-deletable'
$env:ANDROID_SDK_ROOT  = $env:ANDROID_HOME
$env:ANDROID_USER_HOME = Join-Path $Tool 'gradle-home-cache-deletable\android-user-home'
$env:GRADLE_USER_HOME  = Join-Path $Tool 'gradle-home-cache-deletable'
$env:GRADLE_OPTS       = '-Dfile.encoding=UTF-8'
$GradleBin             = Join-Path $Tool 'gradle-home-cache-deletable\gradle-dist\gradle-9.4.1\bin'
$env:PATH              = "$env:JAVA_HOME\bin;$GradleBin;$env:ANDROID_HOME\cmdline-tools\latest\bin;$env:ANDROID_HOME\platform-tools;" + $env:PATH

# Direct download is fastest here; the local proxy is 60-90x slower for Google hosts.
$env:HTTP_PROXY  = ''
$env:HTTPS_PROXY = ''
$env:NO_PROXY    = '*'

$env:BUILD_DIR   = Join-Path $Tool 'ws-gradle-build-copy-deletable\tiny_container'
$env:CACHE_DIR   = Join-Path $Tool 'cache-downloads-deletable'
$env:OUTPUT_DIR  = Join-Path $Tool 'out-apk-keep-forever'
$env:SOURCE_DIR  = Join-Path $Root 'apps-tiny-container-v423-source'
$env:AVNC_DIR    = Join-Path $Root 'avnc-upstream-fork-deletable'
