
Name "GamerMacro Pro v6.1"
OutFile "GamerMacro-Pro-Setup.exe"
InstallDir "$PROGRAMFILES\GamerMacro Pro"
RequestExecutionLevel admin

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\GamerMacro Pro\*.*"
  CreateDirectory "$SMPROGRAMS\GamerMacro Pro"
  CreateShortCut "$SMPROGRAMS\GamerMacro Pro\GamerMacro Pro.lnk" "$INSTDIR\GamerMacro Pro.exe"
  CreateShortCut "$DESKTOP\GamerMacro Pro.lnk" "$INSTDIR\GamerMacro Pro.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  RMDir /r "$SMPROGRAMS\GamerMacro Pro"
  Delete "$DESKTOP\GamerMacro Pro.lnk"
  RMDir /r "$INSTDIR"
SectionEnd
