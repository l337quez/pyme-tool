"""
Plugin: Sample Analysis
========================
Manages the sample retention book, certificates of analysis,
lots, and analysis methods for pharmaceutical or laboratory use.

Folder: plugins/sample_analysis/
"""

import os
import sys

# Make sure the root pyme-tool path is accessible for plugin_base imports
_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from plugin_base import BasePlugin
from plugins.sample_analysis import database as db

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt


class Plugin(BasePlugin):
    name         = "Sample Analysis"
    icon         = "icon.png"
    show_in_home = True
    tab_label    = "Sample Analysis"

    def create_widget(self) -> QWidget:
        # Initialize DB (creates tables + seeds dummy data if first run)
        db.init_db()

        # Import views here to avoid circular import issues at load time
        from plugins.sample_analysis.ui.analysis_method_view import AnalysisMethodView
        from plugins.sample_analysis.ui.lot_view              import LotView
        from plugins.sample_analysis.ui.retention_book_view   import RetentionBookView
        from plugins.sample_analysis.ui.certificate_view      import CertificateView

        root = QWidget()
        root.setObjectName("SampleAnalysisPlugin")
        root.setStyleSheet("""
            #SampleAnalysisPlugin { background: #f5f6fa; }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background: #f5f6fa;
            }
            QTabBar::tab {
                background: #ecf0f1;
                color: #7f8c8d;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #e0e0e0;
                font-size: 13px;
                font-weight: bold;
                margin-right: 3px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
            }
            QTabBar::tab:hover:!selected { background: #dde4ea; }
        """)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        # Store view references so on_activated can refresh them
        self._retention_view   = RetentionBookView()
        self._certificate_view = CertificateView()
        self._lot_view         = LotView()
        self._method_view      = AnalysisMethodView()

        tabs.addTab(self._retention_view,   "📋  Retention Book")
        tabs.addTab(self._certificate_view, "🧪  Certificates")
        tabs.addTab(self._lot_view,         "📦  Lots")
        tabs.addTab(self._method_view,      "⚙️  Analysis Methods")

        # Refresh the active view when switching internal tabs
        tabs.currentChanged.connect(self._on_internal_tab_changed)

        layout.addWidget(tabs)
        self._tabs = tabs
        return root

    def _on_internal_tab_changed(self, index: int):
        views = [
            self._retention_view,
            self._certificate_view,
            self._lot_view,
            self._method_view,
        ]
        if 0 <= index < len(views):
            views[index].load_table()

    def on_activated(self):
        """Called when the user navigates to this plugin's tab in the main window."""
        current = self._tabs.currentIndex()
        self._on_internal_tab_changed(current)
