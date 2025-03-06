# Distribution Guide for File Compression Application

This guide provides comprehensive instructions for packaging and distributing the File Compression application as a professional software product.

## Table of Contents
1. [Packaging the Application](#1-packaging-the-application)
2. [Creating Installers](#2-creating-installers)
3. [Managing Dependencies](#3-managing-dependencies)
4. [Distribution Options](#4-distribution-options)
5. [Version Management](#5-version-management)
6. [Update Mechanisms](#6-update-mechanisms)
7. [Licensing Considerations](#7-licensing-considerations)
8. [Troubleshooting](#8-troubleshooting)

## 1. Packaging the Application

### 1.1 Using PyInstaller

[PyInstaller](https://www.pyinstaller.org/) is recommended for creating standalone executables from the File Compression application.

#### Basic PyInstaller Usage

```bash
# Install PyInstaller
pip install pyinstaller

# Generate a single executable file
pyinstaller --onefile --windowed --icon=resources/icons/app_icon.ico main.py

# Generate a more reliable directory-based executable
pyinstaller --name "File Compression" --windowed --icon=resources/icons/app_icon.ico main.py
```

#### Creating a PyInstaller Specification File

For more control, create a spec file:

```bash
# Generate a spec file
pyi-makespec --name "File Compression" --windowed --icon=resources/icons/app_icon.ico main.py
```

Edit the generated spec file (`File Compression.spec`):

```python
# Example modifications to the spec file
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),  # Include resources directory
        ('ui/styles', 'ui/styles'),  # Include styles
        ('LICENSE', '.'),            # Include license file
    ],
    hiddenimports=['PyQt5.sip'],     # Add hidden imports
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)
```

Build using the spec file:

```bash
pyinstaller "File Compression.spec"
```

### 1.2 Alternative Packaging Tools

#### cx_Freeze

```bash
pip install cx_Freeze
```

Create a `setup.py` file:

```python
import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "PyQt5", "sys", "huffman", "lzw", "deflate", "compression", "ui"],
    "include_files": [
        "resources/",
        "ui/styles/",
        "LICENSE"
    ],
    "excludes": ["tkinter"]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="File Compression",
    version="1.0.0",
    description="File Compression Application",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="resources/icons/app_icon.ico")]
)
```

Build with cx_Freeze:

```bash
python setup.py build
```

#### py2exe (Windows only)

```bash
pip install py2exe
```

Create a `setup.py` file:

```python
from distutils.core import setup
import py2exe

setup(
    windows=[{"script": "main.py", "icon_resources": [(1, "resources/icons/app_icon.ico")]}],
    options={
        "py2exe": {
            "packages": ["huffman", "lzw", "deflate", "compression", "ui"],
            "includes": ["PyQt5.sip"],
            "dll_excludes": ["MSVCP90.dll"],
            "bundle_files": 1
        }
    },
    data_files=[
        ("resources", ["resources/*"]),
        ("ui/styles", ["ui/styles/*"]),
        ("", ["LICENSE"])
    ],
    zipfile=None
)
```

Build with py2exe:

```bash
python setup.py py2exe
```

## 2. Creating Installers

### 2.1 Windows Installers

#### Inno Setup

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Create an Inno Setup script (`.iss` file):

```iss
; File Compression Application Installer Script
#define MyAppName "File Compression"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://www.yourcompany.com"
#define MyAppExeName "File Compression.exe"

[Setup]
AppId={{B8A57F38-C6D3-4E9A-A38F-013E25D0232A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=FileCompression_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppName}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
```

3. Compile the script to create the installer.

#### NSIS (Nullsoft Scriptable Install System)

1. Download and install [NSIS](https://nsis.sourceforge.io/)
2. Create an NSIS script (`.nsi` file):

```nsi
; File Compression Application NSIS Script
!define APPNAME "File Compression"
!define COMPANYNAME "Your Company Name"
!define DESCRIPTION "A file compression application"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

!define HELPURL "https://www.yourcompany.com/help"
!define UPDATEURL "https://www.yourcompany.com/update"
!define ABOUTURL "https://www.yourcompany.com/about"

RequestExecutionLevel admin

Name "${APPNAME}"
OutFile "FileCompression_Setup.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
InstallDirRegKey HKLM "Software\${APPNAME}" "Install_Dir"

!include "MUI2.nsh"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath $INSTDIR
    File /r "dist\${APPNAME}\*.*"
    File "LICENSE"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\${APPNAME}.exe,0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${APPNAME}.exe"
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${APPNAME}.exe"
SectionEnd

Section "Uninstall"
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$DESKTOP\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR"
    
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
```

3. Compile the script with NSIS.

### 2.2 macOS Packaging

#### Creating a macOS .app Bundle

1. Use PyInstaller to create a macOS app:

```bash
pyinstaller --name "File Compression" --windowed --icon=resources/icons/app_icon.icns main.py
```

2. Create a DMG installer with `create-dmg`:

```bash
brew install create-dmg
create-dmg \
    --volname "File Compression" \
    --volicon "resources/icons/app_icon.icns" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "File Compression.app" 200 190 \
    --hide-extension "File Compression.app" \
    --app-drop-link 600 185 \
    "File Compression.dmg" \
    "dist/File Compression.app"
```

### 2.3 Linux Packaging

#### Debian/Ubuntu Packages

1. Install required tools:

```bash
sudo apt-get install python3-stdeb dh-python
```

2. Create a `setup.py` if not already created:

```python
from setuptools import setup, find_packages

setup(
    name="file-compression",
    version="1.0.0",
    packages=find_packages(),
    scripts=["main.py"],
    install_requires=["PyQt5", "zlib", "bz2file"],
    package_data={
        "": ["resources/*", "ui/styles/*", "LICENSE"],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="File Compression Application",
    keywords="compression, huffman, lzw, deflate",
    url="https://www.yourcompany.com",
)
```

3. Build a Debian package:

```bash
python3 setup.py --command-packages=stdeb.command bdist_deb
```

#### RPM Packages (Fedora, CentOS, RHEL)

```bash
pip install rpm-generator
python setup.py bdist_rpm
```

## 3. Managing Dependencies

### 3.1 Identifying Dependencies

Use `pipreqs` or `pip freeze` to identify required dependencies:

```bash
pip install pipreqs
pipreqs /path/to/project --force
```

Create a `requirements.txt` file for your application:

```
PyQt5==5.15.6
zlib==1.2.11
bz2file==0.98
```

### 3.2 Embedding Dependencies

When using PyInstaller, dependencies are typically bundled automatically. To ensure this works correctly:

1. Use the `--hidden-import` flag for any imports that PyInstaller might miss:

```bash
pyinstaller --hidden-import=huffman.huffman --hidden-import=lzw.lzw main.py
```

2. Specify data files in your spec file:

```python
datas=[
    ('resources', 'resources'),
    ('ui/styles', 'ui/styles')
]
```

### 3.3 Virtual Environments

For development and build purposes, use virtual environments:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 4. Distribution Options

### 4.1 Direct Download

Host your installers on your website or a file hosting service:

1. Create a downloads page with clear instructions
2. Include system requirements
3. Provide checksums (MD5, SHA256) for security verification

Example HTML for download page:

```html
<div class="downloads">
    <h2>Download File Compression</h2>
    <div class="download-option">
        <h3>Windows</h3>
        <a href="downloads/FileCompression_Setup.exe" class="download-button">Download for Windows</a>
        <p>SHA256: <code>3a7e5e...</code></p>
    </div>
    <div class="download-option">
        <h3>macOS</h3>
        <a href="downloads/FileCompression.dmg" class="download-button">Download for macOS</a>
        <p>SHA256: <code>6b8d2c...</code></p>
    </div>
    <div class="download-option">
        <h3>Linux</h3>
        <a href="

