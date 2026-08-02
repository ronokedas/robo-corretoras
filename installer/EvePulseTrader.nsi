Unicode True
!include "MUI2.nsh"
!include "x64.nsh"

!define PRODUCT "EvePulse Trader"
!define VERSION "1.0.3"
!define PUBLISHER "EvePulse"

Name "${PRODUCT}"
OutFile "..\release\EvePulseTrader-Setup-${VERSION}.exe"
InstallDir "$PROGRAMFILES64\EvePulse Trader"
InstallDirRegKey HKLM "Software\EvePulse Trader" "InstallDir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
Icon "..\assets\evepulse.ico"
UninstallIcon "..\assets\evepulse.ico"
BrandingText "EvePulse • Tecnologia para decisões inteligentes"

!define MUI_ABORTWARNING
!define MUI_ICON "..\assets\evepulse.ico"
!define MUI_UNICON "..\assets\evepulse.ico"
!define MUI_WELCOMEPAGE_TITLE "Bem-vindo ao EvePulse Trader"
!define MUI_WELCOMEPAGE_TEXT "Este assistente instalará o EvePulse Trader ${VERSION}.\r\n\r\nMonitoramento inteligente da estratégia M1 para ativos OTC."
!define MUI_FINISHPAGE_RUN "$INSTDIR\EvePulseTrader.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Abrir EvePulse Trader"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "PortugueseBR"

Section "Aplicativo" SEC_APP
  SetOutPath "$INSTDIR"
  File /r "..\dist\EvePulseTrader\*"
  WriteRegStr HKLM "Software\EvePulse Trader" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EvePulseTrader" "DisplayName" "${PRODUCT}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EvePulseTrader" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EvePulseTrader" "Publisher" "${PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EvePulseTrader" "DisplayIcon" "$INSTDIR\EvePulseTrader.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EvePulseTrader" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateDirectory "$SMPROGRAMS\EvePulse Trader"
  CreateShortcut "$SMPROGRAMS\EvePulse Trader\EvePulse Trader.lnk" "$INSTDIR\EvePulseTrader.exe"
  CreateShortcut "$SMPROGRAMS\EvePulse Trader\Desinstalar.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section /o "Atalho na área de trabalho" SEC_DESKTOP
  CreateShortcut "$DESKTOP\EvePulse Trader.lnk" "$INSTDIR\EvePulseTrader.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\EvePulse Trader.lnk"
  RMDir /r "$SMPROGRAMS\EvePulse Trader"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\EvePulse Trader"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EvePulseTrader"
SectionEnd
