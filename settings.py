import json
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QFrame, 
                             QMessageBox, QStackedWidget, QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtPrintSupport import QPrinterInfo
from printers.manager import PrinterManager
import sqlite3
import uuid

class SidebarButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)
        self.setText(f" {icon_text}  {text}")
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 20px;
                font-size: 14px;
                font-weight: bold;
                color: #ecf0f1;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                margin: 5px 10px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
            }
        """)

class BusinessPage(QWidget):
    def __init__(self, settings_path):
        super().__init__()
        self.settings_path = settings_path
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        title = QLabel("Datos del Negocio")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        descr = QLabel("Esta información aparecerá en la cabecera de tus tickets de venta.")
        descr.setStyleSheet("color: #7f8c8d; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(descr)

        form_frame = QFrame()
        form_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 25px; }")
        form_layout = QVBoxLayout(form_frame)
        
        self.name_input = self.create_input("Nombre del Negocio:", "Ej: Mi Tienda S.A.S", form_layout)
        self.address_input = self.create_input("Dirección:", "Ej: Calle 123 #45-67", form_layout)
        self.phone_input = self.create_input("Teléfono:", "Ej: +57 300 123 4567", form_layout)
        self.id_input = self.create_input("NIT / RIF / ID:", "Ej: 900.123.456-1", form_layout)

        layout.addWidget(form_frame)

        save_btn = QPushButton("Guardar Cambios")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setFixedWidth(200)
        save_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 12px; border-radius: 8px; font-size: 14px; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        layout.addWidget(save_btn)
        layout.addStretch()

    def create_input(self, label_text, placeholder, parent_layout):
        row = QVBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 13px; color: #34495e; font-weight: bold; border: none; background: transparent;")
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet("padding: 5px 10px; min-height: 30px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px;")
        row.addWidget(label)
        row.addWidget(input_field)
        parent_layout.addLayout(row)
        return input_field

    def save_settings(self):
        data = {}
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        data.update({
            "business_name": self.name_input.text(),
            "address": self.address_input.text(),
            "phone": self.phone_input.text(),
            "business_id": self.id_input.text()
        })
        
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Éxito", "Datos del negocio guardados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

class PrinterPage(QWidget):
    def __init__(self, settings_path):
        super().__init__()
        self.settings_path = settings_path
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        title = QLabel("Configuración de Impresora")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_frame = QFrame()
        form_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 25px; }")
        form_layout = QVBoxLayout(form_frame)

        # 1. Driver
        driver_label = QLabel("Driver de Impresora:")
        driver_label.setStyleSheet("font-weight: bold; color: #34495e; border: none; background: transparent;")
        self.driver_combo = QComboBox()
        self.driver_combo.setStyleSheet("padding: 5px 10px; min-height: 30px; border: 1px solid #ccc; border-radius: 5px;")
        drivers = PrinterManager.get_available_drivers()
        self.driver_combo.addItems(list(drivers.keys()))
        form_layout.addWidget(driver_label)
        form_layout.addWidget(self.driver_combo)

        # 2. System Printer
        system_printer_label = QLabel("Impresora del Sistema (Windows):")
        system_printer_label.setStyleSheet("font-weight: bold; color: #34495e; margin-top: 15px; border: none; background: transparent;")
        self.printer_combo = QComboBox()
        self.printer_combo.setStyleSheet("padding: 5px 10px; min-height: 30px; border: 1px solid #ccc; border-radius: 5px;")
        available_printers = [p.printerName() for p in QPrinterInfo.availablePrinters()]
        self.printer_combo.addItems(available_printers)
        form_layout.addWidget(system_printer_label)
        form_layout.addWidget(self.printer_combo)
        
        bt_note = QLabel("<i>Nota: Vincula tu impresora Bluetooth (GOOJPRT) en Windows antes de buscarla aquí.</i>")
        bt_note.setStyleSheet("font-size: 11px; color: #7f8c8d; margin-top: 5px; border: none; background: transparent;")
        form_layout.addWidget(bt_note)

        # 3. Auto-print
        self.autoprint_check = QCheckBox("Activar impresión automática al guardar venta")
        self.autoprint_check.setStyleSheet("font-size: 13px; color: #34495e; padding: 15px 0;")
        form_layout.addWidget(self.autoprint_check)

        layout.addWidget(form_frame)

        save_btn = QPushButton("Guardar Configuración")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setFixedWidth(200)
        save_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 12px; border-radius: 8px; font-size: 14px; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        layout.addWidget(save_btn)
        layout.addStretch()

    def save_settings(self):
        data = {}
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        data["driver_name"] = self.driver_combo.currentText()
        data["printer_name"] = self.printer_combo.currentText()
        data["auto_print"] = self.autoprint_check.isChecked()
        
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Éxito", "Configuración de impresora guardada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

class GenericManagementPage(QWidget):
    def __init__(self, title_text, table_name, fields):
        super().__init__()
        self.table_name = table_name
        self.fields = fields # Lista de tuples (id_sqlite, label, placeholder, type_widget)
        
        self.conexion_db = sqlite3.connect('pyme_tool_data_base.db')
        self.cursor = self.conexion_db.cursor()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # -- Lado Izquierdo: Lista y Búsqueda --
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        list_layout.addWidget(title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input.textChanged.connect(self.load_data)
        self.search_input.setStyleSheet("padding: 5px 10px; min-height: 30px; border: 1px solid #ccc; border-radius: 5px;")
        list_layout.addWidget(self.search_input)
        
        from PySide6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem
        self.table = QTableWidget()
        headers = [f[1] for f in self.fields]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellClicked.connect(self.load_item_to_form)
        list_layout.addWidget(self.table)
        
        layout.addWidget(list_container, 2)

        # -- Lado Derecho: Formulario --
        form_container = QFrame()
        form_container.setFixedWidth(300)
        form_container.setStyleSheet("QFrame { background-color: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 15px; }")
        form_layout = QVBoxLayout(form_container)
        
        form_title = QLabel("Detalles")
        form_title.setStyleSheet("font-weight: bold; border: none;")
        form_layout.addWidget(form_title)
        
        self.inputs = {}
        for db_col, label_text, placeholder, widget_type in self.fields:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 11px; color: #7f8c8d; border: none; margin-top: 5px;")
            form_layout.addWidget(lbl)
            
            if widget_type == "combo":
                w = QComboBox()
                w.addItems(["Dinero Fiat", "Criptomoneda"])
            else:
                w = QLineEdit()
                w.setPlaceholderText(placeholder)
            
            w.setStyleSheet("padding: 5px 10px; min-height: 30px; border: 1px solid #ddd; border-top: none; border-left: none; border-right: none;")
            form_layout.addWidget(w)
            self.inputs[db_col] = w
            
        self.current_id = None
        
        btn_layout = QVBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.save_item)
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        
        self.new_btn = QPushButton("Nuevo / Limpiar")
        self.new_btn.clicked.connect(self.clear_form)
        self.new_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px; border-radius: 5px;")
        
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.clicked.connect(self.delete_item)
        self.delete_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px;")
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.new_btn)
        btn_layout.addWidget(self.delete_btn)
        form_layout.addLayout(btn_layout)
        form_layout.addStretch()
        
        layout.addWidget(form_container, 1)
        
        self.load_data()

    def load_data(self):
        txt = self.search_input.text()
        cols = [f[0] for f in self.fields]
        query = f"SELECT id, {', '.join(cols)} FROM {self.table_name} WHERE " + " OR ".join([f"{c} LIKE ?" for c in cols])
        params = tuple([f"%{txt}%" for _ in cols])
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        from PySide6.QtWidgets import QTableWidgetItem
        self.table.setRowCount(0)
        self.all_rows_data = {} # store data by row index
        
        for i, row_data in enumerate(rows):
            self.table.insertRow(i)
            self.all_rows_data[i] = row_data
            for j, val in enumerate(row_data[1:]):
                item_text = "Cripto" if val == 1 and self.fields[j][3] == "combo" else ("Fiat" if val == 0 and self.fields[j][3] == "combo" else str(val if val is not None else ""))
                self.table.setItem(i, j, QTableWidgetItem(item_text))

    def load_item_to_form(self, row, col):
        data = self.all_rows_data.get(row)
        if data:
            self.current_id = data[0]
            for i, (db_col, _, _, w_type) in enumerate(self.fields):
                val = data[i+1]
                if w_type == "combo":
                    self.inputs[db_col].setCurrentIndex(int(val if val is not None else 0))
                else:
                    self.inputs[db_col].setText(str(val if val is not None else ""))

    def clear_form(self):
        self.current_id = None
        for db_col, _, _, w_type in self.fields:
            if w_type == "combo":
                self.inputs[db_col].setCurrentIndex(0)
            else:
                self.inputs[db_col].setText("")
        self.table.clearSelection()

    def save_item(self):
        cols = [f[0] for f in self.fields]
        vals = []
        for db_col, _, _, w_type in self.fields:
            if w_type == "combo":
                vals.append(self.inputs[db_col].currentIndex())
            else:
                vals.append(self.inputs[db_col].text())
        
        if self.current_id:
            set_clause = ", ".join([f"{c} = ?" for c in cols])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
            self.cursor.execute(query, tuple(vals) + (self.current_id,))
        else:
            placeholders = ", ".join(["?" for _ in cols])
            query = f"INSERT INTO {self.table_name} ({', '.join(cols)}) VALUES ({placeholders})"
            self.cursor.execute(query, tuple(vals))
        
        self.conexion_db.commit()
        QMessageBox.information(self, "Éxito", "Registro guardado correctamente.")
        self.clear_form()
        self.load_data()

    def delete_item(self):
        if not self.current_id:
            return
        
        res = QMessageBox.question(self, "Confirmar", "¿Seguro que desea eliminar este registro?", QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (self.current_id,))
            self.conexion_db.commit()
            self.clear_form()
            self.load_data()

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_path = 'settings.json'
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #2c3e50; border: none;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(0)

        logo_label = QLabel("⚙️ AJUSTES")
        logo_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; margin-bottom: 30px; padding-left: 20px;")
        sidebar_layout.addWidget(logo_label)

        self.btn_negocio = SidebarButton("Negocio", "🏠")
        self.btn_impresora = SidebarButton("Impresora", "🖨️")
        self.btn_vendedores = SidebarButton("Vendedores", "👤")
        self.btn_clientes = SidebarButton("Clientes", "🤝")
        self.btn_monedas = SidebarButton("Monedas", "💰")
        
        sidebar_layout.addWidget(self.btn_negocio)
        sidebar_layout.addWidget(self.btn_impresora)
        sidebar_layout.addWidget(self.btn_vendedores)
        sidebar_layout.addWidget(self.btn_clientes)
        sidebar_layout.addWidget(self.btn_monedas)
        sidebar_layout.addStretch()

        # --- Content Area ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #f5f6fa;")
        
        self.business_page = BusinessPage(self.settings_path)
        self.printer_page = PrinterPage(self.settings_path)
        
        self.vendedores_page = GenericManagementPage(
            "Gestión de Vendedores", "sellers", 
            [("name", "Nombre", "Ej: Juan Pérez", "text"),
             ("phone", "Teléfono", "Ej: 123456", "text"),
             ("sector", "Sector/Dirección", "Ej: Centro", "text"),
             ("cedula", "ID/Cédula", "Ej: V-12.345.678", "text")]
        )
        
        self.clientes_page = GenericManagementPage(
            "Gestión de Clientes", "clients", 
            [("name", "Nombre", "Ej: Pedro Pérez", "text"),
             ("phone", "Teléfono", "Ej: 123456", "text"),
             ("sector", "Sector/Dirección", "Ej: Centro", "text"),
             ("cedula", "ID/Cédula", "Ej: V-12.345.678", "text")]
        )
        
        self.monedas_page = GenericManagementPage(
            "Gestión de Monedas", "currencies", 
            [("name", "Nombre", "Ej: Dólar", "text"),
             ("symbol", "Símbolo", "Ej: $", "text"),
             ("is_crypto", "Tipo", "", "combo")]
        )
        
        self.stacked_widget.addWidget(self.business_page)
        self.stacked_widget.addWidget(self.printer_page)
        self.stacked_widget.addWidget(self.vendedores_page)
        self.stacked_widget.addWidget(self.clientes_page)
        self.stacked_widget.addWidget(self.monedas_page)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)

        # Connections
        self.btn_negocio.clicked.connect(lambda: self.switch_page(0))
        self.btn_impresora.clicked.connect(lambda: self.switch_page(1))
        self.btn_vendedores.clicked.connect(lambda: self.switch_page(2))
        self.btn_clientes.clicked.connect(lambda: self.switch_page(3))
        self.btn_monedas.clicked.connect(lambda: self.switch_page(4))
        
        # Initial State
        self.switch_page(0)
        self.load_all_data()

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.btn_negocio.setChecked(index == 0)
        self.btn_impresora.setChecked(index == 1)
        self.btn_vendedores.setChecked(index == 2)
        self.btn_clientes.setChecked(index == 3)
        self.btn_monedas.setChecked(index == 4)

    def load_all_data(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load Business Info
                    self.business_page.name_input.setText(data.get("business_name", ""))
                    self.business_page.address_input.setText(data.get("address", ""))
                    self.business_page.phone_input.setText(data.get("phone", ""))
                    self.business_page.id_input.setText(data.get("business_id", ""))
                    
                    # Load Printer Info
                    idx_driver = self.printer_page.driver_combo.findText(data.get("driver_name", ""))
                    if idx_driver != -1: self.printer_page.driver_combo.setCurrentIndex(idx_driver)
                    
                    idx_printer = self.printer_page.printer_combo.findText(data.get("printer_name", ""))
                    if idx_printer != -1: self.printer_page.printer_combo.setCurrentIndex(idx_printer)
                    
                    self.printer_page.autoprint_check.setChecked(data.get("auto_print", False))
            except Exception:
                pass
