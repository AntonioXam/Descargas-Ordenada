#define MyAppName "DescargasOrdenadas"
#define MyAppVersion GetEnv("APP_VERSION")
#define MyAppPublisher "AntonioXam"
#define MyAppExeName "DescargasOrdenadas.exe"

[Setup]
AppId={{7C5E6E3B-9F7C-4E1A-9F2A-5D8F5F5C5B5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=..\..\dist\instalador
OutputBaseFilename=DescargasOrdenadas-Setup-v{#MyAppVersion}
SetupIconFile=..\..\resources\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\..\dist\DescargasOrdenadas\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent
