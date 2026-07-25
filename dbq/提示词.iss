; 专门为"绘画提示辅助器"定制的安装脚本
[Setup]
; 基本信息
AppName=绘画提示辅助器
AppVersion=1.6
AppPublisher=极速的光小喵
DefaultDirName={userappdata}\AI_Prompt_Generator
DefaultGroupName=绘画提示辅助器
UninstallDisplayIcon={app}\AI_Prompt_Generator.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=no
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
LicenseFile=E:\我的九儿猫\绘画提示辅助器\免责声明.txt

; 输出位置（安装包生成到哪里）
OutputDir=E:\我的九儿猫\绘画提示辅助器\dist
OutputBaseFilename=绘画提示辅助器_Setup_v1.6_新人模式版

[Files]
Source: "E:\我的九儿猫\绘画提示辅助器\dist\AI_Prompt_Generator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "E:\我的九儿猫\绘画提示辅助器\免责声明.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\绘画提示辅助器"; Filename: "{app}\AI_Prompt_Generator.exe"
Name: "{userdesktop}\绘画提示辅助器"; Filename: "{app}\AI_Prompt_Generator.exe"

[Run]
Filename: "{app}\AI_Prompt_Generator.exe"; Description: "运行绘画提示辅助器"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
; Type: filesandordirs; Name: "{app}\data"
