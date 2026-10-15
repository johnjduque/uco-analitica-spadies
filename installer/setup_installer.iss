; Inno Setup Script for UCO MAP Analytics Desktop System
; Script generated for Windows Desktop Installation

[Setup]
AppId={{D37B40A1-9E28-44A6-A221-972109BC8205}
AppName=UCO MAP Analytics
AppVersion=1.0.0
AppPublisher=Universidad Católica de Oriente
AppPublisherURL=https://www.uco.edu.co
AppSupportURL=https://www.uco.edu.co
AppUpdatesURL=https://www.uco.edu.co
DefaultDirName={autopf}\UCO_MAP_Analytics
DefaultGroupName=UCO MAP Analytics
DisableProgramGroupPage=yes
OutputBaseFilename=Setup_UcoMap_Analytics
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\UcoMapAnalytics.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Data\*"; DestDir: "{app}\Data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\UCO MAP Analytics"; Filename: "{app}\UcoMapAnalytics.exe"
Name: "{autodesktop}\UCO MAP Analytics"; Filename: "{app}\UcoMapAnalytics.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\UcoMapAnalytics.exe"; Description: "{cm:LaunchProgram,UCO MAP Analytics}"; Flags: nowait postinstall skipifsilent
