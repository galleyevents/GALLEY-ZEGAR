; Skrypt Inno Setup: buduje jeden plik GALLEY-Zegar-Setup.exe
; Wymaga wcześniejszego zbudowania programu (dist\GalleyZegar) przez PyInstaller (zegar.spec).

#define AppName "GALLEY Zegar"
#define AppVersion "1.2"
#define AppExe "GalleyZegar.exe"

[Setup]
; Własny AppId (NIE ten z GALLEY Presentation Manager): osobny program, osobna instalacja i deinstalacja.
; NIE zmieniać - kolejne wersje aktualizują instalację w miejscu.
AppId={{2BC2F645-D233-4E32-B028-139FC61E8A7F}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=GALLEY
DefaultDirName={autopf}\GALLEY Zegar
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
; Instalacja bez uprawnień administratora (z opcją dla wszystkich użytkowników)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=instalator
OutputBaseFilename=GALLEY-Zegar-Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
SetupIconFile=zegar.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "dist\GalleyZegar\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"; Comment: "Zegar czasu wystąpienia na pełnym ekranie (do kluczowania w vMixie)"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
