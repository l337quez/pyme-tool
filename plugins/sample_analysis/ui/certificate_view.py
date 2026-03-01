"""
certificate_view.py
====================
CRUD view for certificate_of_analysis table.
"""

import sys, os, random, string
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from plugins.sample_analysis import database as db
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QFrame, QMessageBox, QHeaderView,
    QComboBox, QTextEdit, QScrollArea, QFileDialog, QSplitter
)
from PySide6.QtCore import Qt


STYLE = """
    QPushButton#BtnNew    { background:#3498db;color:white;border-radius:8px;padding:8px 18px;font-weight:bold;border:none; }
    QPushButton#BtnNew:hover    { background:#2980b9; }
    QPushButton#BtnSave   { background:#2ecc71;color:white;border-radius:8px;padding:8px 18px;font-weight:bold;border:none; }
    QPushButton#BtnSave:hover   { background:#27ae60; }
    QPushButton#BtnDelete { background:#e74c3c;color:white;border-radius:8px;padding:8px 18px;font-weight:bold;border:none; }
    QPushButton#BtnDelete:hover { background:#c0392b; }
    QPushButton#BtnFile   { background:#9b59b6;color:white;border-radius:8px;padding:6px 12px;font-weight:bold;border:none; }
    QPushButton#BtnFile:hover   { background:#8e44ad; }
    QPushButton#BtnGen    { background:#9b59b6;color:white;border-radius:8px;padding:6px 12px;font-weight:bold;border:none; }
    QPushButton#BtnGen:hover    { background:#8e44ad; }
    QLineEdit,QComboBox { border:1px solid #d5dbdb;border-radius:6px;padding:6px 10px;font-size:13px;color:#2c3e50; }
    QLineEdit:focus,QComboBox:focus { border:1px solid #3498db; }
    QTextEdit { border:1px solid #d5dbdb;border-radius:6px;padding:6px 10px;font-size:13px;color:#2c3e50; }
    QTextEdit:focus { border:1px solid #3498db; }
    QTableWidget { border:1px solid #e0e0e0;border-radius:8px;background:white;gridline-color:#f0f0f0;font-size:13px;color:#2c3e50; }
    QHeaderView::section { background:#f5f6fa;color:#7f8c8d;font-weight:bold;font-size:12px;border:none;padding:8px;border-bottom:1px solid #e0e0e0; }
"""

LBL_W = 150


def _lbl(text):
    l = QLabel(text)
    l.setFixedWidth(LBL_W)
    l.setStyleSheet("font-size:13px;color:#7f8c8d;font-weight:bold;")
    return l


class CertificateView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLE)
        self._editing_id = None
        self._build_ui()
        self.load_table()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        header = QLabel("🧪  Certificates of Analysis")
        header.setStyleSheet("font-size:20px;font-weight:bold;color:#2c3e50;")
        root.addWidget(header)

        # Splitter: table on top, form on bottom
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)

        # ── Table ───────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Analysis #", "Date", "Pharmacist", "Business ID", "Method"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._on_select)
        self.table.setMinimumHeight(180)
        splitter.addWidget(self.table)

        # ── Form (scrollable) ────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        form_widget = QWidget()
        form_widget.setObjectName("FormFrame")
        form_widget.setStyleSheet(
            "#FormFrame{background:white;border-radius:10px;border:1px solid #e0e0e0;}"
        )
        fl = QVBoxLayout(form_widget)
        fl.setContentsMargins(16, 16, 16, 16)
        fl.setSpacing(10)

        self.form_title = QLabel("New Certificate")
        self.form_title.setStyleSheet("font-size:14px;font-weight:bold;color:#2c3e50;")
        fl.addWidget(self.form_title)

        def row_line(label, placeholder=""):
            r = QHBoxLayout()
            r.addWidget(_lbl(label))
            f = QLineEdit(); f.setPlaceholderText(placeholder)
            r.addWidget(f)
            fl.addLayout(r)
            return f

        def row_combo(label):
            r = QHBoxLayout()
            r.addWidget(_lbl(label))
            c = QComboBox()
            r.addWidget(c)
            fl.addLayout(r)
            return c

        def row_text(label):
            r = QHBoxLayout()
            r.addWidget(_lbl(label))
            t = QTextEdit(); t.setFixedHeight(70)
            r.addWidget(t)
            fl.addLayout(r)
            return t

        def row_file(label):
            r = QHBoxLayout()
            r.addWidget(_lbl(label))
            f = QLineEdit(); f.setReadOnly(True)
            btn = QPushButton("Browse..."); btn.setObjectName("BtnFile")
            btn.setFixedWidth(90)
            r.addWidget(f); r.addWidget(btn)
            fl.addLayout(r)
            return f, btn

        # Analysis Number: text field + Generate button
        r_an = QHBoxLayout()
        r_an.addWidget(_lbl("Analysis Number *"))
        self.f_analysis = QLineEdit()
        self.f_analysis.setPlaceholderText("Type or generate a 7-digit code")
        self.btn_gen_cert = QPushButton("Generate")
        self.btn_gen_cert.setObjectName("BtnGen")
        self.btn_gen_cert.setFixedWidth(90)
        self.btn_gen_cert.clicked.connect(self._generate_cert_number)
        r_an.addWidget(self.f_analysis)
        r_an.addWidget(self.btn_gen_cert)
        fl.addLayout(r_an)

        self.f_date     = row_line("Date *",             "YYYY-MM-DD")
        self.f_pharma   = row_line("Pharmacist Regent *","Full name")
        self.f_biz      = row_line("Business ID",        "e.g. RNC-001")
        self.f_method   = row_combo("Analysis Method")
        self.f_results  = row_text("Results")
        self.f_obs      = row_text("Observation")
        self.f_attach, btn_attach = row_file("Attachment")
        self.f_sig,    btn_sig    = row_file("Signature Image")

        btn_attach.clicked.connect(lambda: self._pick_file(self.f_attach, "All Files (*.*)"))
        btn_sig.clicked.connect(lambda: self._pick_file(self.f_sig, "Images (*.png *.jpg *.bmp)"))

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

        scroll.setWidget(form_widget)
        splitter.addWidget(scroll)
        splitter.setSizes([200, 400])

        root.addWidget(splitter)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _pick_file(self, field: QLineEdit, filt: str):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", filt)
        if path:
            field.setText(path)

    def _populate_combos(self):
        # Analysis methods only (analysis_number is now a free text field)
        self._method_list = db.get_all_analysis_methods()
        self.f_method.clear()
        self.f_method.addItem("— None —", None)
        for m in self._method_list:
            self.f_method.addItem(f"{m['code']} – {m['name']}", m["id"])

    def _generate_cert_number(self):
        """Generate a unique random 7-digit certificate analysis number."""
        existing = {r["analysis_number"] for r in db.get_all_certificates()}
        for _ in range(100):
            code = "".join(random.choices(string.digits, k=7))
            if code not in existing:
                self.f_analysis.setText(code)
                return
        QMessageBox.warning(self, "Error", "Could not generate a unique code. Try again.")

    def load_table(self):
        self._rows = db.get_all_certificates()
        self.table.setRowCount(len(self._rows))
        for i, r in enumerate(self._rows):
            self.table.setItem(i, 0, QTableWidgetItem(r["analysis_number"]))
            self.table.setItem(i, 1, QTableWidgetItem(r["date"] or ""))
            self.table.setItem(i, 2, QTableWidgetItem(r["pharmacist_regent"] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(r["business_id"] or ""))
            self.table.setItem(i, 4, QTableWidgetItem(r["method_name"] or ""))
        self._populate_combos()
        self._clear_form()

    def _clear_form(self):
        self._editing_id = None
        self.form_title.setText("New Certificate")
        self.f_analysis.clear()
        self.f_date.clear(); self.f_pharma.clear(); self.f_biz.clear()
        self.f_results.clear(); self.f_obs.clear()
        self.f_attach.clear(); self.f_sig.clear()
        self.f_method.setCurrentIndex(0)
        self.btn_delete.setEnabled(False)

    def _on_select(self):
        if not self.table.selectedItems():
            return
        idx = self.table.currentRow()
        r = self._rows[idx]
        self._editing_id = r["id"]
        self.form_title.setText("Edit Certificate")
        self.f_date.setText(r["date"] or "")
        self.f_pharma.setText(r["pharmacist_regent"] or "")
        self.f_biz.setText(r["business_id"] or "")
        self.f_results.setPlainText(r["results"] or "")
        self.f_obs.setPlainText(r["observation"] or "")
        self.f_attach.setText(r["attachment"] or "")
        self.f_sig.setText(r["signature_image"] or "")

        self.f_analysis.setText(r["analysis_number"] or "")

        for i in range(self.f_method.count()):
            if self.f_method.itemData(i) == r["analysis_method_id"]:
                self.f_method.setCurrentIndex(i); break

        self.btn_delete.setEnabled(True)

    def _on_new(self):
        self.table.clearSelection()
        self._clear_form()

    def _on_save(self):
        an   = self.f_analysis.text().strip()
        date = self.f_date.text().strip()
        pharma = self.f_pharma.text().strip()
        if not an:
            QMessageBox.warning(self, "Validation", "Analysis Number is required. Type or generate one.")
            return
        if not date or not pharma:
            QMessageBox.warning(self, "Validation", "Date and Pharmacist Regent are required.")
            return

        data = {
            "analysis_number":    an,
            "date":               date,
            "pharmacist_regent":  pharma,
            "business_id":        self.f_biz.text().strip() or None,
            "results":            self.f_results.toPlainText().strip() or None,
            "observation":        self.f_obs.toPlainText().strip() or None,
            "attachment":         self.f_attach.text().strip() or None,
            "signature_image":    self.f_sig.text().strip() or None,
            "analysis_method_id": self.f_method.currentData(),
        }
        try:
            db.save_certificate(data, self._editing_id)
            self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_delete(self):
        if not self._editing_id:
            return
        if QMessageBox.question(self, "Confirm", "Delete this certificate?") == QMessageBox.Yes:
            db.delete_certificate(self._editing_id)
            self.load_table()
