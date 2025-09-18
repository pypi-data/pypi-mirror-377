#!/usr/bin/env python3
"""
Command-line interface for SnipText
"""

import sys
import argparse
from PyQt5.QtWidgets import QApplication
from .app import SnipTextApp


def main():
    """Main entry point for the SnipText application"""
    parser = argparse.ArgumentParser(
        description="SnipText",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sniptext                    # Start the application in system tray
  sniptext --version          # Show version information
  sniptext --help             # Show this help message

The application will start in the system tray. Right-click the tray icon
to access the screenshot functionality.
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='SnipText 1.0.0'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with console output'
    )
    
    args = parser.parse_args()
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("SnipText")
    app.setApplicationVersion("1.0.0")
    app.setApplicationDisplayName("SnipText - Extract Text from Screenshot")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Prevent app from quitting when last window is closed (for system tray)
    app.setQuitOnLastWindowClosed(False)
    
    # Create main window
    try:
        window = SnipTextApp()
        
        if args.debug:
            print("SnipText started in debug mode")
            print("Look for the camera icon in your system tray")
            print("Right-click the icon to take screenshots")
        
        # Start the application
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error starting SnipText: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
