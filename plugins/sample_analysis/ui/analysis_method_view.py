"""
analysis_method_view.py
========================
Editable table view for the analysis_method table.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from plugins.sample_analysis import database as db
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QFrame, QMessageBox, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt


STYLE = """
    QPushButton#BtnNew {
        background: #3498db; color: white; border-radius: 8px;
        padding: 8px 18px; font-weight: bold; border: none;
    }
    QPushButton#BtnNew:hover { background: #2980b9; }
    QPushButton#BtnSave {
        background: #2ecc71; color: white; border-radius: 8px;
        padding: 8px 18px; font-weight: bold; border: none;
    }
    QPushButton#BtnSave:hover { background: #27ae60; }
    QPushButton#BtnDelete {
        background: #e74c3c; color: white; border-radius: 8px;
        padding: 8px 18px; font-weight: bold; border: none;
    }
    QPushButton#BtnDelete:hover { background: #c0392b; }
    QLineEdit {
        border: 1px solid #d5dbdb; border-radius: 6px;
        padding: 6px 10px; font-size: 13px; color: #2c3e50;
    }
    QLineEdit:focus { border: 1px solid #3498db; }
    QTableWidget {
        border: 1px solid #e0e0e0; border-radius: 8px;
        background: white; gridline-color: #f0f0f0;
        font-size: 13px; color: #2c3e50;
    }
    QHeaderView::section {
        background: #f5f6fa; color: #7f8c8d;
        font-weight: bold; font-size: 12px;
        border: none; padding: 8px;
        border-bottom: 1px solid #e0e0e0;
    }
"""


def form_field(label_text):
    row = QHBoxLayout()
    lbl = QLabel(label_text)
    lbl.setFixedWidth(110)
    lbl.setStyleSheet("font-size: 13px; color: #7f8c8d; font-weight: bold;")
    field = QLineEdit()
    row.addWidget(lbl)
    row.addWidget(field)
    return row, field


class AnalysisMethodView(QWidget):
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

        # Header
        header = QLabel("⚙️  Analysis Methods")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Code", "Specification"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        # Form frame
        self.form_frame = QFrame()
        self.form_frame.setObjectName("FormFrame")
        self.form_frame.setStyleSheet("""
            #FormFrame { background: white; border-radius: 10px;
                         border: 1px solid #e0e0e0; }
        """)
        form_layout = QVBoxLayout(self.form_frame)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(10)

        self.form_title = QLabel("New Method")
        self.form_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        form_layout.addWidget(self.form_title)

        row1, self.f_name = form_field("Name")
        row2, self.f_code = form_field("Code")
        row3, self.f_spec = form_field("Specification")
        form_layout.addLayout(row1)
        form_layout.addLayout(row2)
        form_layout.addLayout(row3)

        btn_row = QHBoxLayout()
        self.btn_new    = QPushButton("New");    self.btn_new.setObjectName("BtnNew")
        self.btn_save   = QPushButton("Save");   self.btn_save.setObjectName("BtnSave")
        self.btn_delete = QPushButton("Delete"); self.btn_delete.setObjectName("BtnDelete")
        btn_row.addWidget(self.btn_new)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_delete)
        form_layout.addLayout(btn_row)

        self.btn_new.clicked.connect(self._on_new)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_delete.clicked.connect(self._on_delete)

        layout.addWidget(self.form_frame)

    # ── Data ────────────────────────────────────────────────────────────────

    def load_table(self):
        self._rows = db.get_all_analysis_methods()
        self.table.setRowCount(len(self._rows))
        for i, row in enumerate(self._rows):
            self.table.setItem(i, 0, QTableWidgetItem(row["name"]))
            self.table.setItem(i, 1, QTableWidgetItem(row["code"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["specification"] or ""))
        self._clear_form()

    def _clear_form(self):
        self._editing_id = None
        self.form_title.setText("New Method")
        self.f_name.clear(); self.f_code.clear(); self.f_spec.clear()
        self.btn_delete.setEnabled(False)

    # ── Slots ────────────────────────────────────────────────────────────────

    def _on_select(self):
        rows = self.table.selectedItems()
        if not rows:
            return
        idx = self.table.currentRow()
        record = self._rows[idx]
        self._editing_id = record["id"]
        self.form_title.setText("Edit Method")
        self.f_name.setText(record["name"])
        self.f_code.setText(record["code"])
        self.f_spec.setText(record["specification"] or "")
        self.btn_delete.setEnabled(True)

    def _on_new(self):
        self.table.clearSelection()
        self._clear_form()

    def _on_save(self):
        name = self.f_name.text().strip()
        code = self.f_code.text().strip()
        spec = self.f_spec.text().strip()
        if not name or not code:
            QMessageBox.warning(self, "Validation", "Name and Code are required.")
            return
        try:
            db.save_analysis_method(name, code, spec or None, self._editing_id)
            self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_delete(self):
        if not self._editing_id:
            return
        reply = QMessageBox.question(self, "Confirm", "Delete this analysis method?")
        if reply == QMessageBox.Yes:
            db.delete_analysis_method(self._editing_id)
            self.load_table()
