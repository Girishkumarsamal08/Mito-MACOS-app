#!/bin/bash
set -e

echo "=== Terminating Any Running MITO Instances ==="
pkill -9 -f "MITO" || true
pkill -9 -f "Main.py" || true

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

echo "=== Copying Character Resource Videos & Generating AppIcon ==="
cp ../Resources/*.mp4 "$APP_DIR/Contents/Resources/"

if [ -f "../Resources/logo.png" ] || [ -f "../Resources/APP_LOGO.png" ]; then
    echo "Generating AppIcon.icns from logo.png..."
    python3 -c "
import os, subprocess
from PIL import Image

logo_path = '../Resources/logo.png' if os.path.exists('../Resources/logo.png') else '../Resources/APP_LOGO.png'
iconset_dir = '../Resources/AppIcon.iconset'
icns_path = '../Resources/AppIcon.icns'

os.makedirs(iconset_dir, exist_ok=True)
img = Image.open(logo_path).convert('RGBA')

w, h = img.size
max_dim = max(w, h)
square_img = Image.new('RGBA', (max_dim, max_dim), (0, 0, 0, 0))
square_img.paste(img, ((max_dim - w) // 2, (max_dim - h) // 2))

specs = [
    ('icon_16x16.png', 16),
    ('icon_16x16@2x.png', 32),
    ('icon_32x32.png', 32),
    ('icon_32x32@2x.png', 64),
    ('icon_128x128.png', 128),
    ('icon_128x128@2x.png', 256),
    ('icon_256x256.png', 256),
    ('icon_256x256@2x.png', 512),
    ('icon_512x512.png', 512),
    ('icon_512x512@2x.png', 1024)
]

for filename, sz in specs:
    square_img.resize((sz, sz), Image.LANCZOS).save(os.path.join(iconset_dir, filename))

subprocess.run(['iconutil', '-c', 'icns', iconset_dir, '-o', icns_path], capture_output=True)
subprocess.run(['rm', '-rf', iconset_dir])
"
fi

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
    <string>AppIcon.icns</string>
    <key>CFBundleIconName</key>
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

touch "$APP_DIR"
echo "=== MITO.app Bundle Successfully Created ==="
ls -la "$APP_DIR/Contents/MacOS"

