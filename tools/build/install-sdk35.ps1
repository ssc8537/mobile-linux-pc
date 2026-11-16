$ErrorActionPreference = 'Stop'
$env:HTTPS_PROXY = 'http://127.0.0.1:7897'
$env:HTTP_PROXY  = 'http://127.0.0.1:7897'
$env:JAVA_HOME = "$PWD\build-env-toolchain\jdk21-runtime-deletable\jdk-21.0.13+9"
$env:ANDROID_HOME = "$PWD\build-env-toolchain\sdk-android-platform-tools-deletable"
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
$env:ANDROID_USER_HOME = "$PWD\build-env-toolchain\gradle-home-cache-deletable\android-user-home"
$env:GRADLE_USER_HOME = "$PWD\build-env-toolchain\gradle-home-cache-deletable"
$env:PATH = "$env:JAVA_HOME\bin;$env:ANDROID_HOME\cmdline-tools\latest\bin;$env:ANDROID_HOME\platform-tools;" + $env:PATH

$sdkm = "$env:ANDROID_HOME\cmdline-tools\latest\bin\sdkmanager.bat"
& $sdkm 'platforms;android-35' 'build-tools;35.0.0' 2>&1 | Select-Object -Last 12
"exit=$LASTEXITCODE"
Get-ChildItem "$env:ANDROID_HOME\platforms" | Select-Object Name
Get-ChildItem "$env:ANDROID_HOME\build-tools" | Select-Object Name
