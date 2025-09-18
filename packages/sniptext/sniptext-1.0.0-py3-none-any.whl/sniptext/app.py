import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QWidget, QMessageBox,
                             QSplitter, QFrame, QScrollArea, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
import subprocess
from .ocr import extract_text_from_image


class SnippingWidget(QtWidgets.QWidget):
    """Screen snipping widget for capturing screen areas"""
    screenshot_taken = pyqtSignal(str)  # Signal to emit when screenshot is taken
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setWindowState(QtCore.Qt.WindowFullScreen)

        # Capture full screen with HiDPI scaling
        screen = QtWidgets.QApplication.primaryScreen()
        self.bg_pixmap = screen.grabWindow(0)

        self.snip_rect = QtCore.QRect()
        self.start = QtCore.QPoint()
        self.end = QtCore.QPoint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        # Draw the background screenshot
        painter.drawPixmap(0, 0, self.bg_pixmap)

        # Dim overlay
        dim_color = QtGui.QColor(0, 0, 0, 120)
        painter.fillRect(self.rect(), dim_color)

        # Draw selection rectangle
        if not self.snip_rect.isNull():
            # Fix scaling for Retina displays
            dpr = self.bg_pixmap.devicePixelRatio()
            scaled_src = QtCore.QRect(
                int(self.snip_rect.x() * dpr),
                int(self.snip_rect.y() * dpr),
                int(self.snip_rect.width() * dpr),
                int(self.snip_rect.height() * dpr),
            )

            # Copy selected area from background
            selection = self.bg_pixmap.copy(scaled_src)
            selection.setDevicePixelRatio(1)  # reset for painting

            # Paint preview of selected region
            painter.drawPixmap(self.snip_rect, selection)

            # Draw red border
            pen = QtGui.QPen(QtGui.QColor(255, 0, 0), 2)
            painter.setPen(pen)
            painter.drawRect(self.snip_rect)

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.snip_rect = QtCore.QRect(self.start, self.end).normalized()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.snip_rect = QtCore.QRect(self.start, self.end).normalized()

        if not self.snip_rect.isNull():
            # Save selected screenshot
            dpr = self.bg_pixmap.devicePixelRatio()
            scaled_src = QtCore.QRect(
                int(self.snip_rect.x() * dpr),
                int(self.snip_rect.y() * dpr),
                int(self.snip_rect.width() * dpr),
                int(self.snip_rect.height() * dpr),
            )
            final_img = self.bg_pixmap.copy(scaled_src)
            final_img.setDevicePixelRatio(1)
            
            # Save screenshot with timestamp to avoid conflicts
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshot_{timestamp}.png"
            final_img.save(screenshot_path)
            
            print(f"✅ Screenshot saved: {self.snip_rect.width()}x{self.snip_rect.height()} px")
            
            # Emit signal with screenshot path
            self.screenshot_taken.emit(screenshot_path)

        # Close the snipping widget immediately
        self.close()
        
        # Force the widget to be destroyed
        QTimer.singleShot(100, self.deleteLater)

    def keyPressEvent(self, event):
        # Allow ESC to cancel snipping
        if event.key() == Qt.Key_Escape:
            self.close()
            QTimer.singleShot(100, self.deleteLater)


class OCRWorker(QThread):
    """Worker thread for OCR processing to avoid blocking the UI"""
    ocr_finished = pyqtSignal(str, str)  # Signal with (screenshot_path, extracted_text)
    ocr_error = pyqtSignal(str)  # Signal for errors
    
    def __init__(self, screenshot_path):
        super().__init__()
        self.screenshot_path = screenshot_path
        
    def run(self):
        try:
            extracted_text = extract_text_from_image(self.screenshot_path)
            self.ocr_finished.emit(self.screenshot_path, extracted_text)
        except Exception as e:
            self.ocr_error.emit(str(e))


class SnipTextApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.snipping_widget = None
        self.ocr_worker = None
        self.setup_system_tray()
        
        # Set application icon for dock
        app_icon = self.create_tray_icon()
        self.setWindowIcon(app_icon)
        QApplication.instance().setWindowIcon(app_icon)
        
        # Hide main window by default - it will show when needed
        self.hide()
        
    def init_ui(self):
        self.setWindowTitle("SnipText - Extract Text from Screenshot Tool")
        self.setGeometry(100, 100, 800, 600)
        
        # Set application icon (you can add an icon file later)
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title and description
        title_label = QLabel("SnipText")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        
        description_label = QLabel("Click 'Take Screenshot' to capture a screen area and extract text")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(description_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Take Screenshot button (the main "Snap" button)
        self.snap_button = QPushButton("📸 Take Screenshot")
        self.snap_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.snap_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.snap_button.clicked.connect(self.take_screenshot)
        
        # Clear button
        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.setFont(QFont("Arial", 10))
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_button.clicked.connect(self.clear_text)
        
        # Copy button
        self.copy_button = QPushButton("📋 Copy Text")
        self.copy_button.setFont(QFont("Arial", 10))
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.copy_button.clicked.connect(self.copy_text)
        self.copy_button.setEnabled(False)
        
        button_layout.addWidget(self.snap_button)
        button_layout.addStretch()
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Ready to capture screenshot...")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; margin: 10px;")
        main_layout.addWidget(self.status_label)
        
        # Create splitter for image preview and text
        splitter = QSplitter(Qt.Horizontal)
        
        # Image preview area
        image_frame = QFrame()
        image_frame.setFrameStyle(QFrame.StyledPanel)
        image_layout = QVBoxLayout(image_frame)
        
        image_title = QLabel("Screenshot Preview")
        image_title.setFont(QFont("Arial", 12, QFont.Bold))
        image_title.setAlignment(Qt.AlignCenter)
        
        self.image_label = QLabel("No screenshot taken yet")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                background-color: #ecf0f1;
                color: #7f8c8d;
                padding: 20px;
                border-radius: 8px;
            }
        """)
        self.image_label.setMinimumSize(300, 200)
        self.image_label.setScaledContents(True)
        
        # Scroll area for image
        image_scroll = QScrollArea()
        image_scroll.setWidget(self.image_label)
        image_scroll.setWidgetResizable(True)
        
        image_layout.addWidget(image_title)
        image_layout.addWidget(image_scroll)
        
        # Text output area
        text_frame = QFrame()
        text_frame.setFrameStyle(QFrame.StyledPanel)
        text_layout = QVBoxLayout(text_frame)
        
        text_title = QLabel("Extracted Text")
        text_title.setFont(QFont("Arial", 12, QFont.Bold))
        text_title.setAlignment(Qt.AlignCenter)
        
        self.text_output = QTextEdit()
        self.text_output.setPlaceholderText("Extracted text will appear here...")
        self.text_output.setFont(QFont("Consolas", 10))
        self.text_output.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                background-color: #ffffff;
            }
        """)
        
        text_layout.addWidget(text_title)
        text_layout.addWidget(self.text_output)
        
        # Add frames to splitter
        splitter.addWidget(image_frame)
        splitter.addWidget(text_frame)
        splitter.setSizes([400, 400])  # Equal initial sizes
        
        main_layout.addWidget(splitter)
        
        # Set overall styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                margin: 5px;
            }
        """)
    
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                               "System tray is not available on this system.")
            sys.exit(1)
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create tray icon (using a built-in icon for now)
        icon = self.create_tray_icon()
        self.tray_icon.setIcon(icon)
        
        # Create context menu
        tray_menu = QMenu()
        
        # Take Screenshot action (main action)
        screenshot_action = QAction("Snip and Copy", self)
        screenshot_action.triggered.connect(self.take_screenshot_from_tray)
        screenshot_action.setFont(QFont("Arial", 10, QFont.Bold))  # Make it prominent
        tray_menu.addAction(screenshot_action)
        
        tray_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        # Set the context menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Set tooltip
        self.tray_icon.setToolTip("SnipText - Screenshot OCR Tool")
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Connect double-click to take screenshot
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def create_tray_icon(self):
        """Create a simple tray icon"""
        # Create a simple icon using text
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw a camera-like icon
        painter.setBrush(QtGui.QBrush(QColor(52, 152, 219)))  # Blue color
        painter.setPen(QtGui.QPen(QColor(41, 128, 185), 2))
        painter.drawEllipse(4, 4, 24, 24)
        
        # Draw lens
        painter.setBrush(QtGui.QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(10, 10, 12, 12)
        
        # Draw inner circle
        painter.setBrush(QtGui.QBrush(QColor(52, 152, 219)))
        painter.drawEllipse(13, 13, 6, 6)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.take_screenshot_from_tray()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click - show context menu (handled automatically)
            pass
    
    def take_screenshot_from_tray(self):
        """Take screenshot when triggered from system tray"""
        self.take_screenshot()
    
    def show_main_window(self):
        """Show the main results window"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def copy_last_text_again(self):
        """Copy the last extracted text to clipboard again"""
        text = self.text_output.toPlainText()
        if text and text.strip() and not text.startswith("OCR Error") and text != "No text detected in the image.":
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.tray_icon.showMessage(
                "SnipText",
                "📋 Last text copied to clipboard again!",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.tray_icon.showMessage(
                "SnipText",
                "⚠️ No text available to copy. Take a screenshot first.",
                QSystemTrayIcon.Warning,
                2000
            )
    
    def quit_application(self):
        """Quit the application"""
        if self.ocr_worker and self.ocr_worker.isRunning():
            self.ocr_worker.quit()
            self.ocr_worker.wait()
        QApplication.quit()
    
    def take_screenshot(self):
        """Start the screenshot capture process"""
        self.status_label.setText("Click and drag to select area...")
        self.status_label.setStyleSheet("color: #f39c12; font-weight: bold; margin: 10px;")
        self.snap_button.setEnabled(False)
        
        # Ensure main window is hidden (but don't force hide if already hidden)
        if self.isVisible():
            self.hide()
            # Small delay to ensure window is hidden
            QTimer.singleShot(200, self.start_snipping)
        else:
            # If already hidden, start immediately
            self.start_snipping()
    
    def start_snipping(self):
        """Create and show the snipping widget"""
        # Clean up any existing snipping widget
        if self.snipping_widget:
            self.snipping_widget.close()
            self.snipping_widget.deleteLater()
            self.snipping_widget = None
        
        # Create new snipping widget
        self.snipping_widget = SnippingWidget()
        self.snipping_widget.screenshot_taken.connect(self.process_screenshot)
        self.snipping_widget.show()
        
        # Ensure it's on top and has focus
        self.snipping_widget.raise_()
        self.snipping_widget.activateWindow()
    
    def process_screenshot(self, screenshot_path):
        """Process the captured screenshot silently"""
        self.snap_button.setEnabled(True)
        
        # Clean up the snipping widget
        if self.snipping_widget:
            self.snipping_widget.close()
            self.snipping_widget.deleteLater()
            self.snipping_widget = None
        
        # Load and display the screenshot (for when window is shown later)
        pixmap = QPixmap(screenshot_path)
        if not pixmap.isNull():
            # Scale image to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setStyleSheet("")  # Remove placeholder styling
        
        # Update status (for when window is shown later)
        self.status_label.setText("Processing OCR...")
        self.status_label.setStyleSheet("color: #f39c12; font-weight: bold; margin: 10px;")
        
        # Show processing notification
        self.tray_icon.showMessage(
            "SnipText",
            "🔍 Processing screenshot with OCR...",
            QSystemTrayIcon.Information,
            2000
        )
        
        # Start OCR processing in background thread
        self.ocr_worker = OCRWorker(screenshot_path)
        self.ocr_worker.ocr_finished.connect(self.on_ocr_finished_silent)
        self.ocr_worker.ocr_error.connect(self.on_ocr_error_silent)
        self.ocr_worker.start()
    
    def on_ocr_finished(self, screenshot_path, extracted_text):
        """Handle OCR completion"""
        if extracted_text and extracted_text.strip():
            self.text_output.setText(extracted_text)
            self.copy_button.setEnabled(True)
            self.status_label.setText(f"✅ OCR completed! Extracted {len(extracted_text)} characters.")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; margin: 10px;")
        else:
            self.text_output.setText("No text detected in the image.")
            self.copy_button.setEnabled(False)
            self.status_label.setText("⚠️ No text found in the screenshot.")
            self.status_label.setStyleSheet("color: #e67e22; font-weight: bold; margin: 10px;")
        
        # Clean up screenshot file
        try:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
        except:
            pass  # Ignore cleanup errors
    
    def on_ocr_finished_silent(self, screenshot_path, extracted_text):
        """Handle OCR completion silently - auto-copy to clipboard"""
        # Update UI data (for when window is shown later)
        if extracted_text and extracted_text.strip():
            self.text_output.setText(extracted_text)
            self.copy_button.setEnabled(True)
            self.status_label.setText(f"✅ OCR completed! Text copied to clipboard.")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; margin: 10px;")
            
            # Auto-copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(extracted_text)
            
            # Show success notification
            char_count = len(extracted_text)
            self.tray_icon.showMessage(
                "SnipText - Success!",
                f"📋 Text extracted and copied to clipboard!\n({char_count} characters)",
                QSystemTrayIcon.Information,
                3000
            )
        else:
            self.text_output.setText("No text detected in the image.")
            self.copy_button.setEnabled(False)
            self.status_label.setText("⚠️ No text found in the screenshot.")
            self.status_label.setStyleSheet("color: #e67e22; font-weight: bold; margin: 10px;")
            
            # Show no text notification
            self.tray_icon.showMessage(
                "SnipText - No Text Found",
                "⚠️ No text detected in the screenshot.",
                QSystemTrayIcon.Warning,
                3000
            )
        
        # Clean up screenshot file
        try:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
        except:
            pass  # Ignore cleanup errors
    
    def on_ocr_error_silent(self, error_message):
        """Handle OCR errors silently"""
        # Update UI data (for when window is shown later)
        self.text_output.setText(f"OCR Error: {error_message}")
        self.copy_button.setEnabled(False)
        self.status_label.setText("❌ OCR failed. Please try again.")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; margin: 10px;")
        
        # Show error notification
        self.tray_icon.showMessage(
            "SnipText - Error",
            f"❌ OCR failed: {error_message}",
            QSystemTrayIcon.Critical,
            4000
        )
    
    def on_ocr_error(self, error_message):
        """Handle OCR errors"""
        self.text_output.setText(f"OCR Error: {error_message}")
        self.copy_button.setEnabled(False)
        self.status_label.setText("❌ OCR failed. Please try again.")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; margin: 10px;")
        
        QMessageBox.warning(self, "OCR Error", f"Failed to process image:\n{error_message}")
    
    def copy_text(self):
        """Copy extracted text to clipboard"""
        text = self.text_output.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_label.setText("📋 Text copied to clipboard!")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; margin: 10px;")
    
    def clear_text(self):
        """Clear the text output and image preview"""
        self.text_output.clear()
        self.image_label.clear()
        self.image_label.setText("No screenshot taken yet")
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                background-color: #ecf0f1;
                color: #7f8c8d;
                padding: 20px;
                border-radius: 8px;
            }
        """)
        self.copy_button.setEnabled(False)
        self.status_label.setText("Ready to capture screenshot...")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; margin: 10px;")
    
    def closeEvent(self, event):
        """Handle application close event - hide to tray instead of closing"""
        if self.tray_icon.isVisible():
            # Hide to tray instead of closing
            self.hide()
            event.ignore()
            
            # Show notification on first minimize
            if not hasattr(self, '_first_minimize_shown'):
                self.tray_icon.showMessage(
                    "SnipText",
                    "Application is running in the system tray. "
                    "Right-click the tray icon to access features.",
                    QSystemTrayIcon.Information,
                    3000
                )
                self._first_minimize_shown = True
        else:
            # If tray is not available, actually quit
            self.quit_application()
            event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SnipText")
    app.setApplicationVersion("1.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Prevent app from quitting when last window is closed (for system tray)
    app.setQuitOnLastWindowClosed(False)
    
    window = SnipTextApp()
    # Don't show window initially - it starts in system tray
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
