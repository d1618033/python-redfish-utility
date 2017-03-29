$START_DIR = "$(get-location)"
$product_version = $Env:MTX_PRODUCT_VERSION
if (!"$product_version") {
    $product_version = "9.9.9.9"
}

$build_number = $Env:MTX_BUILD_NUMBER
if (!"$build_number") {
    $build_number = "999"
}

& $START_DIR\packaging\vc\vcredist_x64.exe /q

if( Test-Path $START_DIR\lessmsi ) { Remove-Item $START_DIR\lessmsi -Recurse -Force }
New-Item -ItemType directory -Path .\lessmsi
& 7z x -y -olessmsi .\packaging\lessmsi\lessmsi-v1.3.zip
if ( $LastExitCode ) { exit 1 }

if( Test-Path $START_DIR\python-2.7.11.amd64 ) { Remove-Item $START_DIR\python-2.7.11.amd64 -Recurse -Force }
& $START_DIR\lessmsi\lessmsi x .\packaging\python\python-2.7.11.amd64.msi
if ( $LastExitCode ) { exit 1 }

# Create an exe from the python script
$Env:PYTHONPATH=".\src"
$PYTHON_AMD64 = "${START_DIR}\python-2.7.11.amd64\SourceDir\python.exe"

Set-Location -Path $START_DIR
if( Test-Path .\pywin32.amd64 ) { Remove-Item .\pywin32.amd64 -Recurse -Force }
New-Item -ItemType directory -Path .\pywin32amd64
& 7z x -y -opywin32amd64 .\packaging\pywin32\pywin32-218.win-amd64-py2.7.exe

Move-Item pywin32amd64 pywin32.amd64
Copy-Item "${START_DIR}\pywin32.amd64\PLATLIB\*"  "$(get-location)\python-2.7.11.amd64\SourceDir\Lib\site-packages" -Recurse -Force
New-Item -ItemType directory -Path "$(get-location)\python-2.7.11.amd64\SourceDir\Scripts"
Copy-Item "${START_DIR}\pywin32.amd64\SCRIPTS\*"  "$(get-location)\python-2.7.11.amd64\SourceDir\Scripts" -Recurse -Force
Set-Location -Path "${START_DIR}\python-2.7.11.amd64\SourceDir\Scripts"
& $PYTHON_AMD64 pywin32_postinstall.py "-install"

Set-Location -Path $START_DIR

Function InstallPythonModule($python, $name, $version) {
    Set-Location -Path "${START_DIR}"
    if( Test-Path .\${name} ) { Remove-Item .\${name} -Recurse -Force }
    New-Item -ItemType directory -Path "${START_DIR}\${name}"
    & 7z x -y "-o${name}" .\packaging\ext\${name}-${version}.tar.gz
    & 7z x -y "-o${name}" "${START_DIR}\${name}\dist\${name}-${version}.tar"
    Set-Location -Path "${START_DIR}\${name}\${name}-${version}"
    & $python setup.py install
    Set-Location -Path "${START_DIR}"
}

Function InstallPythonModuleZip($python, $name, $version) {
    Set-Location -Path "${START_DIR}"
    if( Test-Path .\${name} ) { Remove-Item .\${name} -Recurse -Force }
    New-Item -ItemType directory -Path "${START_DIR}\${name}"
    & 7z x -y "-o${name}" .\packaging\ext\${name}-${version}.zip
    Set-Location -Path "${START_DIR}\${name}\${name}-${version}"
    & $python setup.py install
    Set-Location -Path "${START_DIR}"
}

Function InstallPythonModuleBin($python, $name, $version) {
    Set-Location -Path "${START_DIR}"
    if( Test-Path .\${name} ) { Remove-Item .\${name} -Recurse -Force }
    New-Item -ItemType directory -Path "${START_DIR}\${name}"
    & 7z x -y "-o${name}" .\packaging\ext\${name}-${version}.exe
    Set-Location -Path "${START_DIR}\${name}"
    Copy-Item "${START_DIR}\${name}\PLATLIB\*"  "${START_DIR}\python-2.7.11.amd64\SourceDir\Lib\site-packages" -Recurse -Force
	Set-Location -Path "${START_DIR}"
}

InstallPythonModule "$PYTHON_AMD64" "setuptools" "2.2"
InstallPythonModule "$PYTHON_AMD64" "jsonpointer" "1.1"
InstallPythonModule "$PYTHON_AMD64" "six" "1.7.2"
InstallPythonModule "$PYTHON_AMD64" "ply" "3.4"
InstallPythonModule "$PYTHON_AMD64" "decorator" "3.4.0"
InstallPythonModule "$PYTHON_AMD64" "jsonpatch" "1.3"
InstallPythonModule "$PYTHON_AMD64" "jsonpath-rw" "1.3.0"
InstallPythonModuleZip "$PYTHON_AMD64" "recordtype" "1.1"
InstallPythonModule "$PYTHON_AMD64" "urlparse2" "1.1.1"
InstallPythonModuleZip "$PYTHON_AMD64" "pyreadline" "2.1"
InstallPythonModule "$PYTHON_AMD64" "validictory" "1.0.1"
Copy-Item "$Env:MTX_STAGING_PATH\externals\*.zip" "${START_DIR}\packaging\ext"
InstallPythonModuleZip "$PYTHON_AMD64" "python-ilorest-library" "1.9.0"
Set-Location -Path $START_DIR

Function CreateMSI($python, $pythondir, $arch) {
    Set-Location -Path "${START_DIR}"
    if( Test-Path $START_DIR\dist ) { Remove-Item $START_DIR\dist -Recurse -Force }
    if( Test-Path $START_DIR\build ) { Remove-Item $START_DIR\build -Recurse -Force }
    Set-Location -Path $START_DIR
    
    $DOUBLE_START_DIR =  $START_DIR.replace("\", "\\")
    $DOUBLE_PYTHONDIR =  $pythondir.replace("\", "\\")

    cat win32\rdmc-pyinstaller.spec.in | %{$_ -replace '\$pwd',"${DOUBLE_START_DIR}" } | %{$_ -replace '\$pythondir',"${DOUBLE_PYTHONDIR}" } > rdmc-pyinstaller.spec

    # kill the BOM (stupid powershell)
    $MyFile = Get-Content "${START_DIR}\rdmc-pyinstaller.spec"
    $Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding($False)
    [System.IO.File]::WriteAllLines("${START_DIR}\rdmc-pyinstaller.spec", $MyFile, $Utf8NoBomEncoding)

	Set-Location -Path "${START_DIR}\src"
    & $python "${START_DIR}\pyinstaller-3.1.1\pyinstaller.py" --onefile $START_DIR\rdmc-pyinstaller.spec
	& perl C:\ABSbuild\CodeSigning\SignFile.pl "${START_DIR}\src\dist\ilorest.exe"
    Copy-Item "${START_DIR}\src\dist\ilorest.exe" "${START_DIR}\ilorest.exe"
	Copy-Item "$Env:MTX_STAGING_PATH\schemas\*" "${START_DIR}\src\dist\"
	Copy-Item "$Env:MTX_STAGING_PATH\externals\*.dll" "${START_DIR}\src\dist\"
	Copy-Item "${START_DIR}\packaging\packages\*.dll" "${START_DIR}\src\dist\"
	Copy-Item "${START_DIR}\rdmc-windows.conf" "${START_DIR}\src\dist\redfish.conf"
	Copy-Item "${START_DIR}\src\dist" "${START_DIR}" -Recurse -Force

	Set-Location -Path "${START_DIR}"
    $product_version

    cat win32\rdmc.${arch}.wxs | %{$_ -replace '\$product_version',"${product_version}" } > rdmc.wxs
    & c:\ABSbuild\WiX3\candle.exe "-dsrcFolder=$(get-location)" rdmc.wxs
    & c:\ABSbuild\WiX3\light.exe -b $(get-location) rdmc.wixobj -ext WixUIExtension  -out "ilorest-${product_version}-${build_number}.${arch}.msi"

    if ("$Env:MTX_COLLECTION_PATH") {
        & perl C:\ABSbuild\CodeSigning\SignFile.pl "ilorest-${product_version}-${build_number}.${arch}.msi"
        Copy-Item "ilorest-${product_version}-${build_number}.${arch}.msi" "$Env:MTX_COLLECTION_PATH"
    }
    Set-Location -Path "${START_DIR}"
}

& 7z x -y .\packaging\pyinstaller\PyInstaller-3.1.1.zip
Copy-Item "${START_DIR}\pywin32.amd64\PLATLIB\pywin32_system32\*" .
CreateMSI "$PYTHON_AMD64" "${START_DIR}\python-2.7.11.amd64" "x86_64"





