"""
retention_book_view.py
=======================
CRUD view for the retention_book table.
The analysis_number is automatically set to the selected lot's unique_code.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from plugins.sample_analysis import database as db
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QFrame, QMessageBox, QHeaderView, QComboBox
)
from PySide6.QtCore import Qt


STYLE = """
    QPushButton#BtnNew  { background:#3498db;color:white;border-radius:8px;padding:8px 18px;font-weight:bold;border:none; }
    QPushButton#BtnNew:hover  { background:#2980b9; }
    QPushButton#BtnSave { background:#2ecc71;color:white;border-radius:8px;padding:8px 18px;font-weight:bold;border:none; }
    QPushButton#BtnSave:hover { background:#27ae60; }
    QPushButton#BtnDelete { background:#e74c3c;color:white;border-radius:8px;padding:8px 18px;font-weight:bold;border:none; }
    QPushButton#BtnDelete:hover { background:#c0392b; }
    QLineEdit,QComboBox { border:1px solid #d5dbdb;border-radius:6px;padding:6px 10px;font-size:13px;color:#2c3e50; }
    QLineEdit:focus,QComboBox:focus { border:1px solid #3498db; }
    QTableWidget { border:1px solid #e0e0e0;border-radius:8px;background:white;gridline-color:#f0f0f0;font-size:13px;color:#2c3e50; }
    QHeaderView::section { background:#f5f6fa;color:#7f8c8d;font-weight:bold;font-size:12px;border:none;padding:8px;border-bottom:1px solid #e0e0e0; }
"""


class RetentionBookView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLE)
        self._editing_id = None
        self._build_ui()
        self.load_table()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("📋  Retention Book")
        header.setStyleSheet("font-size:20px;font-weight:bold;color:#2c3e50;")
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Analysis Number", "Lot Code", "Product"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        # Form
        self.form_frame = QFrame()
        self.form_frame.setObjectName("FormFrame")
        self.form_frame.setStyleSheet(
            "#FormFrame{background:white;border-radius:10px;border:1px solid #e0e0e0;}"
        )
        fl = QVBoxLayout(self.form_frame)
        fl.setContentsMargins(16, 16, 16, 16)
        fl.setSpacing(10)

        self.form_title = QLabel("New Entry")
        self.form_title.setStyleSheet("font-size:14px;font-weight:bold;color:#2c3e50;")
        fl.addWidget(self.form_title)

        # Lot dropdown — analysis_number = lot unique_code (auto)
        r_lot = QHBoxLayout()
        l_lot = QLabel("Lot *"); l_lot.setFixedWidth(140)
        l_lot.setStyleSheet("font-size:13px;color:#7f8c8d;font-weight:bold;")
        self.f_lot = QComboBox()
        self.f_lot.currentIndexChanged.connect(self._on_lot_changed)
        r_lot.addWidget(l_lot); r_lot.addWidget(self.f_lot)

        # Auto-filled analysis number (read-only display)
        r_num = QHBoxLayout()
        l_num = QLabel("Analysis Number"); l_num.setFixedWidth(140)
        l_num.setStyleSheet("font-size:13px;color:#7f8c8d;font-weight:bold;")
        self.f_analysis = QLineEdit()
        self.f_analysis.setReadOnly(True)
        self.f_analysis.setStyleSheet(
            "border:1px solid #d5dbdb;border-radius:6px;padding:6px 10px;"
            "font-size:13px;color:#7f8c8d;background:#f5f6fa;"
        )
        self.f_analysis.setPlaceholderText("Auto-filled from lot")
        r_num.addWidget(l_num); r_num.addWidget(self.f_analysis)

        fl.addLayout(r_lot)
        fl.addLayout(r_num)

        btn_row = QHBoxLayout()
        self.btn_new    = QPushButton("New");    self.btn_new.setObjectName("BtnNew")
        self.btn_save   = QPushButton("Save");   self.btn_save.setObjectName("BtnSave")
        self.btn_delete = QPushButton("Delete"); self.btn_delete.setObjectName("BtnDelete")
        btn_row.addWidget(self.btn_new)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_delete)
        fl.addLayout(btn_row)

        self.btn_new.clicked.connect(self._on_new)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_delete.clicked.connect(self._on_delete)

        layout.addWidget(self.form_frame)

    def _populate_lot_combo(self, select_lot_id=None):
        self._lot_list = db.get_all_lots()
        self.f_lot.blockSignals(True)
        self.f_lot.clear()
        select_idx = 0
        for i, lot in enumerate(self._lot_list):
            self.f_lot.addItem(f"{lot['unique_code']} – {lot['product']}", lot["id"])
            if select_lot_id and lot["id"] == select_lot_id:
                select_idx = i
        self.f_lot.blockSignals(False)
        self.f_lot.setCurrentIndex(select_idx)
        self._on_lot_changed(select_idx)

    def _on_lot_changed(self, idx):
        """Auto-fill analysis_number with selected lot's unique_code."""
        if 0 <= idx < len(self._lot_list if hasattr(self, '_lot_list') else []):
            self.f_analysis.setText(self._lot_list[idx]["unique_code"])

    def load_table(self):
        self._rows = db.get_all_retention_entries()
        self.table.setRowCount(len(self._rows))
        for i, r in enumerate(self._rows):
            self.table.setItem(i, 0, QTableWidgetItem(r["analysis_number"]))
            self.table.setItem(i, 1, QTableWidgetItem(r["lot_code"]))
            self.table.setItem(i, 2, QTableWidgetItem(r["product"]))
        self._populate_lot_combo()
        self._clear_form()

    def _clear_form(self):
        self._editing_id = None
        self.form_title.setText("New Entry")
        self.btn_delete.setEnabled(False)
        if self.f_lot.count() > 0:
            self.f_lot.setCurrentIndex(0)

    def _on_select(self):
        if not self.table.selectedItems():
            return
        idx = self.table.currentRow()
        r = self._rows[idx]
        self._editing_id = r["id"]
        self.form_title.setText("Edit Entry")
        self._populate_lot_combo(select_lot_id=r["lot_id"])
        self.btn_delete.setEnabled(True)

    def _on_new(self):
        self.table.clearSelection()
        self._clear_form()

    def _on_save(self):
        num = self.f_analysis.text().strip()
        if not num or self.f_lot.count() == 0:
            QMessageBox.warning(self, "Validation", "Please select a Lot first.")
            return
        lot_id = self.f_lot.currentData()
        try:
            db.save_retention_entry(num, lot_id, self._editing_id)
            self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_delete(self):
        if not self._editing_id:
            return
        if QMessageBox.question(self, "Confirm", "Delete this entry? Related certificates will also be removed.") == QMessageBox.Yes:
            try:
                db.delete_retention_entry(self._editing_id)
                self.load_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
