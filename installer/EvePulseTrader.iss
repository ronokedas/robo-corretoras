#define MyAppName "EvePulse Trader"
#define MyAppVersion "1.0.4"
#define MyAppPublisher "EvePulse"
#define MyAppExeName "EvePulseTrader.exe"

[Setup]
AppId={{2CE7A5BA-C1B6-4FCB-93B6-62F11D369582}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\EvePulse Trader
DefaultGroupName=EvePulse Trader
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=EvePulseTrader-Setup-1.0.4
SetupIconFile=..\assets\evepulse.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "..\dist\EvePulseTrader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\EvePulse Trader"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\EvePulse Trader"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos adicionais:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir EvePulse Trader"; Flags: nowait postinstall skipifsilent
