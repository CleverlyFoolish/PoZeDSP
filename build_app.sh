#!/bin/bash

# Build Script for PoZeDSP (macOS)

APP_NAME="PoZeDSP"
MAIN_SCRIPT="main.py"

echo "Building $APP_NAME..."

# Clean previous builds
rm -rf build dist *.spec

# Run PyInstaller
# --noconsole: Don't show terminal window
# --onefile: Create a single executable (PyInstaller handles .app bundle structure automatically on macOS)
# --name: Name of the app
# --clean: Clean PyInstaller cache
# Use full path to pyinstaller in .venv
/Users/sk/PoZeDSP/.venv/bin/pyinstaller --noconsole --onefile --name "$APP_NAME" --clean --windowed "$MAIN_SCRIPT"

echo "Build complete!"
echo "App bundle is located in dist/$APP_NAME.app"
