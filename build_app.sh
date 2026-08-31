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

echo "=== Copying Character Resource Videos & Generating AppIcon ==="
cp ../Resources/*.mp4 "$APP_DIR/Contents/Resources/"

if [ -f "../Resources/APP_LOGO.png" ]; then
    echo "Generating AppIcon.icns from APP_LOGO.png..."
    python3 -c "
import os, subprocess
from PIL import Image

logo_path = '../Resources/APP_LOGO.png'
iconset_dir = '../Resources/AppIcon.iconset'
icns_path = '../Resources/AppIcon.icns'

os.makedirs(iconset_dir, exist_ok=True)
img = Image.open(logo_path).convert('RGBA')

w, h = img.size
max_dim = max(w, h)
square_img = Image.new('RGBA', (max_dim, max_dim), (0, 0, 0, 0))
square_img.paste(img, ((max_dim - w) // 2, (max_dim - h) // 2))

sizes = [16, 32, 64, 128, 256, 512, 1024]
for s in sizes:
    resized = square_img.resize((s, s), Image.LANCZOS)
    resized.save(os.path.join(iconset_dir, f'icon_{s}x{s}.png'))
    if s <= 512:
        resized_2x = square_img.resize((s * 2, s * 2), Image.LANCZOS)
        resized_2x.save(os.path.join(iconset_dir, f'icon_{s}x{s}@2x.png'))

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
