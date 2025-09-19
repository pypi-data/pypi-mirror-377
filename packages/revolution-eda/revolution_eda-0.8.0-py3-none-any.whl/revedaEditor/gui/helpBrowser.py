import sys
from PySide6.QtCore import QRunnable, Slot, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QDialog,
    QLabel,
    QPushButton,
)

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWebEngineWidgets import (
    QWebEngineView,
)
from PySide6.QtPrintSupport import (
    QPrintDialog,
    QPrinter,
    QPrintPreviewDialog,
)
from revedaEditor.gui.startThread import startThread

class helpBrowser(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.initUI()

    def initUI(self):
        """
        Initializes the UI of the Help Browser window.
        """
        # Set window title
        self.setWindowTitle("Help Browser")

        # Set window geometry
        self.setGeometry(100, 100, 800, 600)

        # Create central widget
        self.centralW = QWidget(self)

        # Create layout for central widget
        layout = QVBoxLayout(self.centralW)

        # Create web view
        webView = QWebEngineView()

        # Add web view to layout
        layout.addWidget(webView)

        # Set central widget
        self.setCentralWidget(self.centralW)

        # Create menu bar
        menuBar = self.menuBar()

        # Create 'Print' menu
        printMenu = menuBar.addMenu("Print")

        # Create print action
        printIcon = QIcon(":/icons/printer--arrow.png")
        self.printAction = QAction(printIcon, "Print...", self)

        # Create print preview action
        printPreviewIcon = QIcon(":/icons/printer--arrow.png")
        self.printPreviewAction = QAction(printPreviewIcon, "Print Preview...", self)

        # Connect print action to printClick method
        self.printAction.triggered.connect(self.printClick)

        # Connect print preview action to printPreviewClick method
        self.printPreviewAction.triggered.connect(self.printPreviewClick)

        # Add print and print preview actions to print menu
        printMenu.addAction(self.printAction)
        printMenu.addAction(self.printPreviewAction)

        # Set local documentation file
        import pathlib
        docsPath = pathlib.Path(__file__).parent.parent.parent / "docs" / "index.md"
        if docsPath.exists():
            try:
                import markdown
                with open(docsPath, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                html_content = markdown.markdown(md_content)
                self.centralW.layout().itemAt(0).widget().setHtml(html_content)
            except ImportError:
                # Fallback: display as plain text in HTML
                with open(docsPath, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                html_content = f"<pre>{md_content}</pre>"
                self.centralW.layout().itemAt(0).widget().setHtml(html_content)
        else:
            websiteUrl = "https://reveda.eu/documentation"
            self.centralW.layout().itemAt(0).widget().setUrl(websiteUrl)

    def printClick(self):
        """
        Handles the 'Print' action.
        """
        # Create print dialog
        dlg = QPrintDialog(self)

        # If print dialog is accepted, start printing
        if dlg.exec() == QDialog.Accepted:
            # Get printer
            printer = dlg.printer()

            # Print the web view directly
            webView = self.centralW.layout().itemAt(0).widget()
            webView.print(printer)

    def printPreviewClick(self):
        """
        Handles the 'Print Preview' action.
        """
        # Create printer with screen resolution
        printer = QPrinter(QPrinter.ScreenResolution)

        # Create print preview dialog
        ppdlg = QPrintPreviewDialog(printer, self)

        # Connect paintRequested signal to lambda that calls print
        webView = self.centralW.layout().itemAt(0).widget()
        ppdlg.paintRequested.connect(lambda p: webView.print(p))

        # Show print preview dialog
        ppdlg.exec()


class aboutDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("About Revolution EDA")
        self.setGeometry(100, 100, 400, 200)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # Add information about your application using rich text
        about_label = QLabel(
            "<h2>Revolution EDA</h2>"
            "<p><strong>Version:</strong> 0.8.0</p>"
            "<p><strong>Copyright: Revolution Semiconductor</strong> © 2024</p>"
            "<p><strong>License:</strong> Mozilla Public License 2.0 amended with Commons Clause</p>"
            "<p><strong> Website:</strong> <a href='https://www.reveda.eu'>Revolution EDA</a></p>"
            "<p><strong> GitHub:</strong> <a href='https://github.com/eskiyerli/revedaRelease'>Revolution EDA GitHub Repository</a></p>"
        )
        about_label.setOpenExternalLinks(True)  # Allow clickable links
        layout.addWidget(about_label)
        layout.addSpacing(20)

        # Add a "Close" button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)
