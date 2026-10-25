; Instalador de Windows para UCO Analytics (Inno Setup 6)
; Requiere haber generado antes dist\UcoAnalytics.exe con PyInstaller (ver main.spec).
; Se instala por usuario en %LOCALAPPDATA% para que la base de datos y la llave
; secreta queden en una carpeta con permisos de escritura y privada del usuario.

[Setup]
AppId={{D37B40A1-9E28-44A6-A221-972109BC8205}
AppName=UCO Analytics
AppVersion=3.0.0
AppPublisher=Universidad Católica de Oriente
AppPublisherURL=https://www.uco.edu.co
DefaultDirName={localappdata}\UCO_Analytics
DefaultGroupName=UCO Analytics
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=Setup_UCO_Analytics_3.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\UcoAnalytics.exe

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Iniciar UCO Analytics automáticamente al iniciar sesión en Windows (recomendado en el equipo que sirve a otros usuarios)"; GroupDescription: "Inicio automático:"; Flags: unchecked

[Files]
Source: "dist\UcoAnalytics.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\backend\.env.example"; DestDir: "{app}"; DestName: ".env.example"; Flags: ignoreversion

[Icons]
Name: "{group}\UCO Analytics"; Filename: "{app}\UcoAnalytics.exe"
Name: "{autodesktop}\UCO Analytics"; Filename: "{app}\UcoAnalytics.exe"; Tasks: desktopicon
; Inicio automático: arranca minimizado y sin abrir el navegador (el usuario entra desde su favorito).
Name: "{userstartup}\UCO Analytics"; Filename: "{app}\UcoAnalytics.exe"; Parameters: "--sin-navegador"; Flags: runminimized; Tasks: autostart

[Run]
Filename: "{app}\UcoAnalytics.exe"; Description: "{cm:LaunchProgram,UCO Analytics}"; Flags: nowait postinstall skipifsilent

; Nota: la base de datos (datos_uco.db) y la llave (.secret_key) se conservan al
; desinstalar para no perder información. Elimínelas manualmente si desea un borrado completo.
