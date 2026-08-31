#!/bin/bash
set -e

echo "=== Building MITO Swift Executable ==="
cd "$(dirname "$0")/MITO-macOS"
swift build -c release

BUILD_BIN=".build/release/MITO"
APP_DIR="../MITO.app"

echo "=== Creating MITO.app Bundle Structure ==="
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

cp "$BUILD_BIN" "$APP_DIR/Contents/MacOS/MITO"
chmod +x "$APP_DIR/Contents/MacOS/MITO"

echo "=== Copying Character Resource Videos & AppIcon ==="
cp ../Resources/*.mp4 "$APP_DIR/Contents/Resources/"
if [ -f "../Resources/AppIcon.icns" ]; then
    cp "../Resources/AppIcon.icns" "$APP_DIR/Contents/Resources/"
fi

echo "=== Creating Info.plist ==="
cat << 'EOF' > "$APP_DIR/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>MITO</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.mito.desktop.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>MITO</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>13.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <true/>
    <key>NSMicrophoneUsageDescription</key>
    <string>MITO requires microphone access to listen to your voice commands.</string>
    <key>NSSpeechRecognitionUsageDescription</key>
    <string>MITO requires speech recognition to understand your voice commands.</string>
</dict>
</plist>
EOF

echo "=== MITO.app Bundle Successfully Created ==="
ls -la "$APP_DIR/Contents/MacOS"
