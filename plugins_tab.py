"""
plugins_tab.py
==============
Plugin manager tab — lets users enable/disable plugins and change their icons.

Each plugin can optionally include a plugin.json file with:
    {
      "author": "Your Name",
      "version": "1.0.0",
      "description": "What this plugin does."
    }

Enable/disable changes take effect after restarting the application.
Icon changes take effect immediately on the card; Home card updates on restart.
"""

import os
import json
import importlib.util

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QFileDialog, QMessageBox, QSizePolicy, QDialog,
    QDialogButtonBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import plugin_config as cfg


# ── White-styled message helper ───────────────────────────────────────────────
def _info(parent, title: str, text: str):
    """Show an information dialog with an explicit white background
    to avoid inheriting dark stylesheets from ancestor widgets."""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(QMessageBox.Information)
    msg.setStyleSheet("""
        QMessageBox          { background: #ffffff; }
        QMessageBox QLabel   { color: #2c3e50; font-size: 13px; }
        QPushButton          { background: #3498db; color: white; border-radius: 6px;
                               padding: 6px 18px; font-weight: bold; border: none; }
        QPushButton:hover    { background: #2980b9; }
    """)
    msg.exec()


PLUGINS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")

# ── Styles ────────────────────────────────────────────────────────────────────

CARD_ENABLED_STYLE = """
    QFrame#PluginCard {
        background: white; border: 1px solid #e0e0e0; border-radius: 14px;
    }
"""
CARD_DISABLED_STYLE = """
    QFrame#PluginCard {
        background: #f5f5f5; border: 1px solid #ddd; border-radius: 14px;
    }
"""
BTN_ENABLE = ("background:#2ecc71;color:white;border-radius:8px;"
              "padding:6px 14px;font-weight:bold;border:none;font-size:12px;")
BTN_DISABLE = ("background:#e74c3c;color:white;border-radius:8px;"
               "padding:6px 14px;font-weight:bold;border:none;font-size:12px;")
BTN_BLUE = ("background:#3498db;color:white;border-radius:8px;"
            "padding:6px 14px;font-weight:bold;border:none;font-size:12px;")


# ── Metadata helpers ──────────────────────────────────────────────────────────

def _read_manifest(folder: str) -> dict:
    """Read plugin.json from the plugin folder. Returns {} if missing."""
    path = os.path.join(PLUGINS_DIR, folder, "plugin.json")
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _discover_plugins() -> list[dict]:
    """Scan plugins/ folder and return metadata for each valid plugin."""
    result = []
    if not os.path.isdir(PLUGINS_DIR):
        return result

    for folder in sorted(os.listdir(PLUGINS_DIR)):
        plugin_path = os.path.join(PLUGINS_DIR, folder, "plugin.py")
        if not os.path.isfile(plugin_path):
            continue

        manifest = _read_manifest(folder)
        try:
            spec = importlib.util.spec_from_file_location(
                f"plugins._scan.{folder}", plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            cls = getattr(module, "Plugin")

            result.append({
                "folder":       folder,
                "name":         cls.name,
                "tab_label":    cls.tab_label,
                "show_in_home": cls.show_in_home,
                "default_icon": os.path.join(PLUGINS_DIR, folder, cls.icon),
                "author":       manifest.get("author", "—"),
                "version":      manifest.get("version", "—"),
                "description":  manifest.get("description", ""),
            })
        except Exception as e:
            result.append({
                "folder":       folder,
                "name":         folder,
                "tab_label":    folder,
                "show_in_home": False,
                "default_icon": "",
                "author":       manifest.get("author", "—"),
                "version":      manifest.get("version", "—"),
                "description":  manifest.get("description", ""),
                "error":        str(e),
            })
    return result


# ── Plugin Card ───────────────────────────────────────────────────────────────

class PluginCard(QFrame):
    """Card representing one plugin with enable/disable and icon controls."""

    def __init__(self, meta: dict, parent=None):
        super().__init__(parent)
        self.meta   = meta
        self.folder = meta["folder"]
        self.setObjectName("PluginCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._build()
        self._apply_card_style()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # ── Icon ──────────────────────────────────────────────────────────────
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(60, 60)
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setStyleSheet("border-radius:10px;background:#f0f4f8;")
        self._refresh_icon()
        layout.addWidget(self.icon_lbl)

        # ── Info column ───────────────────────────────────────────────────────
        info = QVBoxLayout()
        info.setSpacing(3)

        # Name + version badge
        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        self.name_lbl = QLabel(self.meta["name"])
        self.name_lbl.setStyleSheet("font-size:15px;font-weight:bold;color:#2c3e50;")
        ver_lbl = QLabel(f"v{self.meta['version']}")
        ver_lbl.setStyleSheet(
            "font-size:11px;color:#fff;background:#3498db;border-radius:6px;"
            "padding:2px 7px;font-weight:bold;"
        )
        name_row.addWidget(self.name_lbl)
        name_row.addWidget(ver_lbl)
        name_row.addStretch()

        # Author + folder
        meta_lbl = QLabel(
            f"👤 {self.meta['author']}   •   📁 {self.folder}   •   🗂 {self.meta['tab_label']}"
        )
        meta_lbl.setStyleSheet("font-size:11px;color:#95a5a6;")

        info.addLayout(name_row)
        info.addWidget(meta_lbl)

        # Description
        if self.meta.get("description"):
            desc_lbl = QLabel(self.meta["description"])
            desc_lbl.setStyleSheet("font-size:12px;color:#7f8c8d;")
            desc_lbl.setWordWrap(True)
            info.addWidget(desc_lbl)

        # Error badge
        if "error" in self.meta:
            err_lbl = QLabel(f"⚠ {self.meta['error']}")
            err_lbl.setStyleSheet("font-size:11px;color:#e74c3c;")
            info.addWidget(err_lbl)

        layout.addLayout(info, stretch=1)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)

        self.btn_toggle = QPushButton()
        self.btn_toggle.setFixedWidth(100)
        self.btn_toggle.clicked.connect(self._toggle)
        self._refresh_toggle()

        btn_icon = QPushButton("🖼  Icon")
        btn_icon.setStyleSheet(BTN_BLUE)
        btn_icon.setFixedWidth(100)
        btn_icon.clicked.connect(self._change_icon)

        btn_col.addWidget(self.btn_toggle)
        btn_col.addWidget(btn_icon)
        layout.addLayout(btn_col)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _apply_card_style(self):
        enabled = cfg.is_enabled(self.folder)
        self.setStyleSheet(CARD_ENABLED_STYLE if enabled else CARD_DISABLED_STYLE)
        opacity = "1.0" if enabled else "0.55"
        self.name_lbl.setStyleSheet(
            f"font-size:15px;font-weight:bold;color:#2c3e50;opacity:{opacity};"
        )

    def _refresh_icon(self):
        icon_path = cfg.get_icon(self.folder, self.meta["default_icon"])
        px = QPixmap(icon_path) if icon_path and os.path.isfile(icon_path) else QPixmap()
        if not px.isNull():
            self.icon_lbl.setPixmap(
                px.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.icon_lbl.setText("🔌")
            self.icon_lbl.setStyleSheet("font-size:28px;border-radius:10px;background:#f0f4f8;")

    def _refresh_toggle(self):
        enabled = cfg.is_enabled(self.folder)
        if enabled:
            self.btn_toggle.setText("✓ Enabled")
            self.btn_toggle.setStyleSheet(BTN_ENABLE)
        else:
            self.btn_toggle.setText("✗ Disabled")
            self.btn_toggle.setStyleSheet(BTN_DISABLE)

    def _toggle(self):
        new_state = not cfg.is_enabled(self.folder)
        cfg.set_enabled(self.folder, new_state)
        self._refresh_toggle()
        self._apply_card_style()
        _info(
            self,
            "Restart required",
            f"Plugin «{self.meta['name']}» will be "
            f"{'enabled' if new_state else 'disabled'} after restarting the app."
        )

    def _change_icon(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Icon", "", "Images (*.png *.jpg *.bmp *.ico)"
        )
        if path:
            cfg.set_icon(self.folder, path)
            self._refresh_icon()
            _info(self, "Icon updated",
                  "Icon saved. The Home card icon will update on next restart.")


# ── Plugin Manager Tab ────────────────────────────────────────────────────────

class PluginsTab(QWidget):
    """Tab that lists all discovered plugins with management controls."""

    def __init__(self, reload_callback=None, parent=None):
        super().__init__(parent)
        # Optional callback to reload plugin tabs in the main window
        self._reload_callback = reload_callback
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setStyleSheet("background:#f5f6fa;")

        self._container = QWidget()
        self._container.setStyleSheet("background:#f5f6fa;")

        self._clayout = QVBoxLayout(self._container)
        self._clayout.setContentsMargins(30, 30, 30, 20)
        self._clayout.setSpacing(16)

        # Header
        hrow = QHBoxLayout()
        hdr = QLabel("🔌  Plugin Manager")
        hdr.setStyleSheet("font-size:24px;font-weight:bold;color:#2c3e50;")
        hrow.addWidget(hdr)
        hrow.addStretch()
        self._btn_refresh = QPushButton("↻  Refresh")
        self._btn_refresh.setStyleSheet(BTN_BLUE)
        self._btn_refresh.clicked.connect(self._on_refresh)
        hrow.addWidget(self._btn_refresh)
        self._clayout.addLayout(hrow)

        # Subtitle
        sub = QLabel("Enable or disable plugins and change their icons here.\n"
                     "Enable/disable changes require a restart to take effect.")
        sub.setStyleSheet("font-size:13px;color:#7f8c8d;")
        self._clayout.addWidget(sub)

        # Cards container (separate widget so we can swap it)
        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet("background:transparent;")
        self._cards_vbox = QVBoxLayout(self._cards_widget)
        self._cards_vbox.setContentsMargins(0, 0, 0, 0)
        self._cards_vbox.setSpacing(12)
        self._clayout.addWidget(self._cards_widget)
        self._clayout.addStretch(1)

        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll)

        self._rebuild_cards()

    def _on_refresh(self):
        """Triggered by Refresh button: reload plugin tabs AND refresh the cards view."""
        # First: tell the main window to reload plugin tabs
        if self._reload_callback:
            self._reload_callback()
        # Then: rebuild the cards to reflect new enabled/disabled states
        self._rebuild_cards()

    def _rebuild_cards(self):
        """Clear and rebuild all plugin cards. Called on init and on Refresh."""
        # Remove all existing cards synchronously
        while self._cards_vbox.count():
            item = self._cards_vbox.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        plugins = _discover_plugins()
        if not plugins:
            lbl = QLabel("No plugins found in the plugins/ folder.")
            lbl.setStyleSheet("font-size:14px;color:#95a5a6;")
            lbl.setAlignment(Qt.AlignCenter)
            self._cards_vbox.addWidget(lbl)
        else:
            for meta in plugins:
                card = PluginCard(meta, parent=self._cards_widget)
                self._cards_vbox.addWidget(card)
                card.show()

        # Force the scroll container to recalculate its size
        self._cards_widget.adjustSize()
        self._container.adjustSize()
        self._cards_widget.update()
        self._container.update()
