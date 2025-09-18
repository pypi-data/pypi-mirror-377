# SnipText - Screenshot OCR Tool

[![PyPI version](https://badge.fury.io/py/sniptext.svg)](https://badge.fury.io/py/sniptext)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight desktop application that captures screenshots and extracts text using OCR, automatically copying the extracted text to your clipboard. Perfect for quickly grabbing text from images, PDFs, or any content on your screen.

## ✨ Features

- 📸 **Easy Screenshot Capture**: Click and drag to select any area of your screen
- 🔍 **Advanced OCR**: Extract text from images with high accuracy using RapidOCR
- 📋 **Auto-Copy to Clipboard**: Extracted text is automatically copied - just paste anywhere!
- 🎯 **System Tray Integration**: Runs quietly in your system tray, always accessible
- 🔔 **Smart Notifications**: Get notified when OCR is complete or if no text is found
- ⚡ **Fast & Silent**: No windows pop up - completely silent workflow
- 🖼️ **HiDPI Support**: Works perfectly on high-resolution displays
- 🌐 **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Installation

### Install from PyPI (Recommended)

```bash
pip install sniptext
```


## 💻 Usage

### Command Line

After installation, simply run:

```bash
sniptext
```

The application will start in your system tray. Look for the blue camera icon!


### How to Use

1. **Start the app**: Run `sniptext` in your terminal
2. **Find the tray icon**: Look for a blue camera icon in your system tray
3. **Take a screenshot**: Right-click the icon → "📸 Take Screenshot & Copy Text"
4. **Select area**: Click and drag to select the text area
6. **Paste anywhere**: The text is automatically in your clipboard - just paste with `Ctrl+V` (or `Cmd+V` on Mac)!

### System Tray Menu

| Menu Item | Description |
|-----------|-------------|
| 📸 Take Screenshot & Copy Text | Main action - starts the screenshot process |
| ❌ Quit | Exit the application |

## 🛠️ Requirements

- Python 3.7 or higher
- PyQt5
- RapidOCR
- NumPy
- Pillow

All dependencies are automatically installed when you install SnipText.

## 🖥️ Supported Platforms

- ✅ **Windows** 10/11
- ✅ **macOS** 10.14+ (including Apple Silicon)
- ✅ **Linux** (Ubuntu, Fedora, etc.)

 
Made with ❤️ for productivity enthusiasts who need to quickly extract text from their screens!

**Aaditya Kanjolia**