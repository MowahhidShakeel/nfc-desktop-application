; Inno Setup Script for Elixion Niviu (Offline Installer Version)

[Setup]
AppName=Elixion Niviu Network Configuration Tool
AppVersion=1.0
DefaultDirName={autopf}\Elixion Niviu Network Configuration Tool
DefaultGroupName=Elixion Niviu
UninstallDisplayIcon={app}\Elixion Niviu Network Configuration Tool.exe
OutputDir=installer
OutputBaseFilename=elixion-niviu-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
; Packages the main application from the PyInstaller dist folder
Source: "dist/Elixion Niviu Network Configuration Tool/*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "driver\*"; DestDir: "{tmp}\driver"; Flags: recursesubdirs createallsubdirs deleteafterinstall
Source: "vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\Elixion Niviu"; Filename: "{app}\Elixion Niviu Network Configuration Tool.exe"
Name: "{autodesktop}\Elixion Niviu"; Filename: "{app}\Elixion Niviu Network Configuration Tool.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Run]
; Runs the prerequisite installer before your application starts.
; The 'Check' flag calls the function in the [Code] section to see if this step is even needed.
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installing Microsoft VC++ Redistributable..."; Check: VCRedistNeedsInstall
Filename: "{tmp}\driver\Setup.exe"; StatusMsg: "Installing NFC Reader Driver...";

; This line runs your actual application after installation is complete.
Filename: "{app}\Elixion Niviu Network Configuration Tool.exe"; Description: "{cm:LaunchProgram,Elixion Niviu}"; Flags: nowait postinstall skipifsilent

[Code]
function VCRedistNeedsInstall: Boolean;
var
  Version: String;
begin
  // This function simply checks if the C++ Redistributable is already installed.
  Result := not RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Version', Version);
end;