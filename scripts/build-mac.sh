# must have yd-ui environment activated

# build app
pyinstaller --onefile --windowed --name YD-UI --add-binary "ffmpeg:ffmpeg" --icon images/YD_UI_logo.icns --noconfirm yd-ui.py

# prepare DMG folder
TMP_DMG_DIR=$(mktemp -d) # create tmp dir with random name
cp -R "dist/YD-UI.app" "$TMP_DMG_DIR"
ln -s /Applications "$TMP_DMG_DIR/Applications"

#create dmg
hdiutil create -volname "YD-UI" -srcfolder "$TMP_DMG_DIR" -ov -format UDZO dist/YD-UI.dmg

# remove tmp dir
rm -rf "$TMP_DMG_DIR"