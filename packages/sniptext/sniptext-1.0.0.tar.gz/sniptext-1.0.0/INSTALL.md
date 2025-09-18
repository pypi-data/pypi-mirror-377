# Installation Guide for SnipText

## 📦 Package Structure

Your SnipText project is now properly packaged and ready for distribution! Here's what we've created:

```
snip-text/
├── sniptext/                 # Main package directory
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Main application code
│   ├── ocr.py               # OCR functionality
│   └── cli.py               # Command-line interface
├── setup.py                 # Setup script for pip
├── pyproject.toml           # Modern Python packaging config
├── requirements.txt         # Dependencies
├── README.md                # Documentation
├── LICENSE                  # MIT License
├── MANIFEST.in              # Package file inclusion rules
└── build_and_install.sh     # Build script
```

## 🚀 Installation Methods


### Method to install
```bash
pip install sniptext
```

# Start the application
sniptext



## 📝 Usage After Installation

Once installed, users can simply run:

```bash
sniptext
```

The app will:
1. Start in the system tray (look for blue camera icon)
2. Right-click the icon to access features
3. Click "📸 Take Screenshot & Copy Text"
4. Drag to select area
5. Text automatically copied to clipboard!

## 🐛 Troubleshooting

**Command not found after installation:**
```bash
# Make sure pip bin directory is in PATH
pip show sniptext  # Should show installation details

# Try with python -m
python -m sniptext.cli
```

**Import errors:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Permission issues on macOS:**
- Grant screen recording permissions in System Preferences → Security & Privacy → Screen Recording

## 🎉 You're Done!

Your SnipText tool is now a proper Python package that can be:
- ✅ Installed with `pip install`
- ✅ Distributed on PyPI
- ✅ Used as a command-line tool
- ✅ Imported as a Python library

Congratulations! 🎊
