#define MyAppName "DescargasOrdenadas"
#define MyAppVersion "1.0"
#define MyAppPublisher "Tu Empresa"
#define MyAppURL "https://www.ejemplo.com"
#define MyAppExeName "DescargasOrdenadas.exe"

[Setup]
; NOTA: El valor de AppId identifica de forma única esta aplicación.
; No uses el mismo AppId en instaladores para otras aplicaciones.
AppId={{D0E49E68-1FA9-4E5F-A4B3-12C823BB1D2B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
; Quitamos el comentario si queremos permitir al usuario elegir el directorio
;AllowDirSelect=yes
OutputDir=installer
OutputBaseFilename=DescargasOrdenadas_Installer
SetupIconFile=resources\app_icon.ico
Compression=lzma
SolidCompression=yes
; Requiere privilegios de administrador para instalar (opcional)
;PrivilegesRequired=admin
; Permitimos al usuario elegir entre instalación para todos los usuarios o solo para el usuario actual
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\{#MyAppName}.exe"; DestDir: "{app}"; Flags: ignoreversion
; Añadir archivos adicionales o carpetas si es necesario
; Source: "carpeta\*"; DestDir: "{app}\carpeta"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function InitializeSetup(): Boolean;
var
  V: Integer;
  iResultCode: Integer;
  sUnInstallString: String;
begin
  Result := True;
  if IsUpgrade() then
  begin
    V := MsgBox(ExpandConstant('Se ha detectado una versión anterior de {#MyAppName}. ¿Desea desinstalarla antes de continuar?'), mbInformation, MB_YESNO);
    if V = IDYES then
    begin
      sUnInstallString := GetUninstallString();
      sUnInstallString := RemoveQuotes(sUnInstallString);
      Exec(sUnInstallString, '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, iResultCode);
      Result := True;
    end;
  end;
end; 