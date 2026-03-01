"""
lot_view.py
===========
CRUD view for the lot table.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from plugins.sample_analysis import database as db
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QFrame, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt


STYLE = """
    QPushButton#BtnNew  { background:#3498db;color:white;border-radius:8px;padding:8px 18px;font-weight:bold;border:none; }
    QPushButton#BtnNew:hover  { background:#2980b9; }
    QPushButton#BtnSave { background:#2ecc71;color:white;border-radius:8px;padding:8px 18px;font-weight:bold;border:none; }
    QPushButton#BtnSave:hover { background:#27ae60; }
    QPushButton#BtnDelete { background:#e74c3c;color:white;border-radius:8px;padding:8px 18px;font-weight:bold;border:none; }
    QPushButton#BtnDelete:hover { background:#c0392b; }
    QLineEdit { border:1px solid #d5dbdb;border-radius:6px;padding:6px 10px;font-size:13px;color:#2c3e50; }
    QLineEdit:focus { border:1px solid #3498db; }
    QTableWidget { border:1px solid #e0e0e0;border-radius:8px;background:white;gridline-color:#f0f0f0;font-size:13px;color:#2c3e50; }
    QHeaderView::section { background:#f5f6fa;color:#7f8c8d;font-weight:bold;font-size:12px;border:none;padding:8px;border-bottom:1px solid #e0e0e0; }
"""


def _field(label_text, placeholder=""):
    row = QHBoxLayout()
    lbl = QLabel(label_text)
    lbl.setFixedWidth(140)
    lbl.setStyleSheet("font-size:13px;color:#7f8c8d;font-weight:bold;")
    f = QLineEdit()
    f.setPlaceholderText(placeholder)
    row.addWidget(lbl)
    row.addWidget(f)
    return row, f


class LotView(QWidget):
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

        header = QLabel("📦  Lots")
        header.setStyleSheet("font-size:20px;font-weight:bold;color:#2c3e50;")
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Unique Code", "Product", "Capacity", "Mfg. Date", "Exp. Date"
        ])
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

        self.form_title = QLabel("New Lot")
        self.form_title.setStyleSheet("font-size:14px;font-weight:bold;color:#2c3e50;")
        fl.addWidget(self.form_title)

        r1, self.f_code  = _field("Unique Code *", "e.g. LOT-2024-001")
        r2, self.f_prod  = _field("Product *",     "Product name")
        r3, self.f_cap   = _field("Capacity",       "e.g. 500 ml")
        r4, self.f_mfg   = _field("Mfg. Date",      "YYYY-MM-DD")
        r5, self.f_exp   = _field("Expiry Date",     "YYYY-MM-DD")
        for r in (r1, r2, r3, r4, r5):
            fl.addLayout(r)

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

    def load_table(self):
        self._rows = db.get_all_lots()
        self.table.setRowCount(len(self._rows))
        for i, r in enumerate(self._rows):
            self.table.setItem(i, 0, QTableWidgetItem(r["unique_code"]))
            self.table.setItem(i, 1, QTableWidgetItem(r["product"]))
            self.table.setItem(i, 2, QTableWidgetItem(r["capacity"] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(r["manufacturing_date"] or ""))
            self.table.setItem(i, 4, QTableWidgetItem(r["expiry_date"] or ""))
        self._clear_form()

    def _clear_form(self):
        self._editing_id = None
        self.form_title.setText("New Lot")
        for f in (self.f_code, self.f_prod, self.f_cap, self.f_mfg, self.f_exp):
            f.clear()
        self.btn_delete.setEnabled(False)

    def _on_select(self):
        if not self.table.selectedItems():
            return
        idx = self.table.currentRow()
        r = self._rows[idx]
        self._editing_id = r["id"]
        self.form_title.setText("Edit Lot")
        self.f_code.setText(r["unique_code"])
        self.f_prod.setText(r["product"])
        self.f_cap.setText(r["capacity"] or "")
        self.f_mfg.setText(r["manufacturing_date"] or "")
        self.f_exp.setText(r["expiry_date"] or "")
        self.btn_delete.setEnabled(True)

    def _on_new(self):
        self.table.clearSelection()
        self._clear_form()

    def _on_save(self):
        code = self.f_code.text().strip()
        prod = self.f_prod.text().strip()
        if not code or not prod:
            QMessageBox.warning(self, "Validation", "Unique Code and Product are required.")
            return
        try:
            db.save_lot(code, prod,
                        self.f_cap.text().strip() or None,
                        self.f_mfg.text().strip() or None,
                        self.f_exp.text().strip() or None,
                        self._editing_id)
            self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_delete(self):
        if not self._editing_id:
            return
        if QMessageBox.question(self, "Confirm", "Delete this lot? This may affect related records.") == QMessageBox.Yes:
            try:
                db.delete_lot(self._editing_id)
                self.load_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
