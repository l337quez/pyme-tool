import sqlite3
import datetime
import json
import os
from printers.manager import PrinterManager
from PySide6.QtWidgets import (QVBoxLayout, QLabel, QLineEdit, QCompleter, QWidget, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QApplication, QDialog, QHeaderView, QAbstractItemView, QFrame, QScrollArea, QGridLayout, QComboBox )
from PySide6.QtCore import (Qt, QObject, QEvent, QSize, Signal)
from PySide6.QtGui import QPixmap

class ProductItemWidget(QFrame):
    clicked = Signal(str) # Emite el nombre del producto

    def __init__(self, name, quantity, price, image_path, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedSize(160, 200)
        self.setStyleSheet("""
            ProductItemWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            ProductItemWidget:hover {
                border: 2px solid #3498db;
                background-color: #f0f8ff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Imagen
        self.image_label = QLabel()
        self.image_label.setFixedSize(140, 110)
        self.image_label.setAlignment(Qt.AlignCenter)
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(140, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_label.setText("N/A")
        else:
            self.image_label.setText("Sin imagen")
        layout.addWidget(self.image_label)
        
        # Nombre
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)
        
        # Info (Stock/Precio)
        self.info_label = QLabel(f"Stock: {quantity} | ${price}")
        self.info_label.setStyleSheet("color: #666; font-size: 11px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        self.product_name = name

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.product_name)

class BaseSearchDialog(QDialog):
    def __init__(self, cursor, title, headers, query, parent=None):
        super().__init__(parent)
        self.cursor = cursor
        self.headers = headers
        self.query = query
        self.setWindowTitle(title)
        self.resize(700, 450)
        
        layout = QVBoxLayout(self)
        
        # Filtro de búsqueda
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText(f"Filtrar {title.lower()}...")
        self.filter_input.textChanged.connect(self.load_data)
        layout.addWidget(self.filter_input)
        
        # Tabla de datos
        self.table = QTableWidget()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.table)
        
        # Botones
        button_layout = QHBoxLayout()
        self.select_button = QPushButton("Seleccionar")
        self.select_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.load_data()
        
    def load_data(self):
        filter_text = self.filter_input.text()
        self.cursor.execute(self.query, ('%' + filter_text + '%',))
        results = self.cursor.fetchall()
        
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table.setItem(row_number, column_number, item)
                
    def get_selected_data(self):
        if self.result() == QDialog.Accepted:
            row = self.table.currentRow()
            if row != -1:
                data = {}
                for i, header in enumerate(self.headers):
                    data[header.lower()] = self.table.item(row, i).text()
                return data
        return None

class ProductSearchDialog(BaseSearchDialog):
    def __init__(self, cursor, parent=None):
        headers = ["Nombre", "Stock", "Precio"]
        query = "SELECT name, quantity, price FROM products WHERE name LIKE ?"
        super().__init__(cursor, "Productos", headers, query, parent)

class SellerSearchDialog(BaseSearchDialog):
    def __init__(self, cursor, parent=None):
        headers = ["Código", "Nombre", "Email", "Dirección", "Tipo"]
        query = "SELECT code, name, email, address, type FROM sellers WHERE name LIKE ? OR code LIKE ?"
        super().__init__(cursor, "Vendedores", headers, query, parent)
    
    def load_data(self):
        filter_text = self.filter_input.text()
        self.cursor.execute(self.query, ('%' + filter_text + '%', '%' + filter_text + '%'))
        results = self.cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

class ClientSearchDialog(BaseSearchDialog):
    def __init__(self, cursor, parent=None):
        headers = ["Código", "Nombre", "Email", "Dirección", "Tipo"]
        query = "SELECT code, name, email, address, type FROM clients WHERE name LIKE ? OR code LIKE ?"
        super().__init__(cursor, "Clientes", headers, query, parent)
    
    def load_data(self):
        filter_text = self.filter_input.text()
        self.cursor.execute(self.query, ('%' + filter_text + '%', '%' + filter_text + '%'))
        results = self.cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

class CurrencySearchDialog(BaseSearchDialog):
    def __init__(self, cursor, parent=None):
        headers = ["Nombre", "Símbolo"]
        query = "SELECT name, symbol FROM currencies WHERE name LIKE ? OR symbol LIKE ?"
        super().__init__(cursor, "Monedas", headers, query, parent)
    
    def load_data(self):
        filter_text = self.filter_input.text()
        self.cursor.execute(self.query, ('%' + filter_text + '%', '%' + filter_text + '%'))
        results = self.cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

class PaymentMethodDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Método de Pago")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Seleccione el método de pago:"))
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Efectivo", "Transferencia", "Crédito"])
        layout.addWidget(self.method_combo)
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Aceptar")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
    def get_method(self):
        return self.method_combo.currentText()

class KeyPressEater(QObject):
    def __init__(self, parent=None):
        super(KeyPressEater, self).__init__(parent)
        self.parent = parent

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                if isinstance(obj, QTableWidget):
                    current_index = obj.currentRow()
                    if current_index != -1:
                        obj.removeRow(current_index)
                        if self.parent:
                            self.parent.calculateTotal()
                        return True
            elif event.key() == Qt.Key_F1:
                if self.parent:
                    self.parent.guardar_venta()
                    return True
            elif event.key() == Qt.Key_F2:
                if self.parent:
                    self.parent.toggle_vendedores()
                    return True
            elif event.key() == Qt.Key_F3:
                if self.parent:
                    self.parent.toggle_clientes()
                    return True
            elif event.key() == Qt.Key_F4:
                if self.parent:
                    self.parent.toggle_monedas()
                    return True
            elif event.key() == Qt.Key_F5:
                if self.parent:
                    self.parent.toggle_creditos()
                    return True
        return False


class SalesTab(QWidget):
    def __init__(self):
        super().__init__()

        # Conexión a la base de datos
        self.conexion_db = sqlite3.connect('pyme_tool_data_base.db')
        self.cursor = self.conexion_db.cursor()

        # Variables internas para datos de F2/F3
        self.vendedor_actual = ""
        self.cliente_actual = ""

        # Configuración del layout principal
        layout = QVBoxLayout()

        # Botones principales en la parte superior
        lh_main = QHBoxLayout()
        
        self.save_btn = QPushButton('Guardar Venta (F1)')
        self.save_btn.clicked.connect(self.guardar_venta)
        self.seller_btn = QPushButton('Vendedores (F2)')
        self.seller_btn.clicked.connect(self.toggle_vendedores)
        self.client_btn = QPushButton('Clientes (F3)')
        self.client_btn.clicked.connect(self.toggle_clientes)
        self.currency_btn = QPushButton('Monedas (F4)')
        self.currency_btn.clicked.connect(self.toggle_monedas)
        self.credit_btn = QPushButton('Créditos (F5)')
        self.credit_btn.clicked.connect(self.toggle_creditos)
        
        for btn in [self.save_btn, self.seller_btn, self.client_btn, self.currency_btn, self.credit_btn]:
            btn.setStyleSheet("font-size: 14px; padding: 10px;")
            lh_main.addWidget(btn)
        
        layout.addLayout(lh_main)

        # Sección de búsqueda
        layout_search = QHBoxLayout()
        self.busqueda_input = QLineEdit()
        self.busqueda_input.setPlaceholderText("Buscar producto por nombre...")
        self.busqueda_input.setStyleSheet("font-size: 16px; padding: 8px;")
        self.busqueda_input.textChanged.connect(self.load_search_grid)
        layout_search.addWidget(self.busqueda_input)
        layout.addLayout(layout_search)

        # Labels informativos de selección
        self.selection_info = QHBoxLayout()
        self.label_vendedor = QLabel("Vendedor: -")
        self.label_cliente = QLabel("Cliente: -")
        self.selection_info.addWidget(self.label_vendedor)
        self.selection_info.addWidget(self.label_cliente)
        layout.addLayout(self.selection_info)

        # SECCIONES INLINE (OCULTAS POR DEFECTO)
        # Contenedor Vendedores
        self.container_vendedores = QWidget()
        self.layout_vendedores = QVBoxLayout(self.container_vendedores)
        self.search_vendedores = QLineEdit()
        self.search_vendedores.setPlaceholderText("Buscar vendedor...")
        self.search_vendedores.textChanged.connect(self.load_vendedores_inline)
        self.table_vendedores = QTableWidget()
        self.table_vendedores.setColumnCount(3)
        self.table_vendedores.setHorizontalHeaderLabels(['Nombre', 'Teléfono', 'Cédula'])
        self.table_vendedores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_vendedores.itemDoubleClicked.connect(self.seleccionar_vendedor_inline)
        self.layout_vendedores.addWidget(self.search_vendedores)
        self.layout_vendedores.addWidget(self.table_vendedores)
        layout.addWidget(self.container_vendedores)
        self.container_vendedores.hide()

        # Contenedor Clientes
        self.container_clientes = QWidget()
        self.layout_clientes = QVBoxLayout(self.container_clientes)
        self.search_clientes = QLineEdit()
        self.search_clientes.setPlaceholderText("Buscar cliente...")
        self.search_clientes.textChanged.connect(self.load_clientes_inline)
        self.table_clientes = QTableWidget()
        self.table_clientes.setColumnCount(3)
        self.table_clientes.setHorizontalHeaderLabels(['Nombre', 'Teléfono', 'Cédula'])
        self.table_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_clientes.itemDoubleClicked.connect(self.seleccionar_cliente_inline)
        self.layout_clientes.addWidget(self.search_clientes)
        self.layout_clientes.addWidget(self.table_clientes)
        layout.addWidget(self.container_clientes)
        self.container_clientes.hide()

        # Contenedor Monedas
        self.container_monedas = QWidget()
        self.layout_monedas = QVBoxLayout(self.container_monedas)
        self.search_monedas = QLineEdit()
        self.search_monedas.setPlaceholderText("Buscar moneda...")
        self.search_monedas.textChanged.connect(self.load_monedas_inline)
        self.table_monedas = QTableWidget()
        self.table_monedas.setColumnCount(3)
        self.table_monedas.setHorizontalHeaderLabels(['Nombre', 'Símbolo', 'Tipo'])
        self.table_monedas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_monedas.itemDoubleClicked.connect(self.seleccionar_moneda_inline)
        self.layout_monedas.addWidget(self.search_monedas)
        self.layout_monedas.addWidget(self.table_monedas)
        layout.addWidget(self.container_monedas)
        self.container_monedas.hide()

        # Contenedor para cuadrícula de productos y tabla de ventas
        layout_middle = QHBoxLayout()
        
        # Cuadrícula de productos (ScrollArea)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_area.setWidget(self.grid_widget)
        layout_middle.addWidget(self.scroll_area, 2) # Proporción 2 para la cuadrícula

        # Tabla de ventas
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Nombre', 'Cantidad', 'Precio'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout_middle.addWidget(self.table, 1) # Proporción 1 para la tabla (más pequeña)
        layout.addLayout(layout_middle)

        # Sección de Créditos Pendientes (Contenedor para Toggle)
        self.container_creditos = QWidget()
        layout_creditos = QVBoxLayout(self.container_creditos)
        layout_creditos.setContentsMargins(0, 10, 0, 0)
        
        label_creditos = QLabel("CRÉDITOS PENDIENTES")
        label_creditos.setStyleSheet("font-weight: bold;")
        layout_creditos.addWidget(label_creditos)
        
        self.table_creditos = QTableWidget()
        self.table_creditos.setColumnCount(6)
        self.table_creditos.setHorizontalHeaderLabels(['ID', 'Fecha', 'Cliente', 'Producto', 'Total', 'Acciones'])
        self.table_creditos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_creditos.addWidget(self.table_creditos)
        
        layout.addWidget(self.container_creditos)
        self.container_creditos.hide() # Oculto por defecto
        
        self.load_creditos()

        # Atalajos de teclado
        self.keyPressEater = KeyPressEater(self)
        self.table.installEventFilter(self.keyPressEater)
        self.installEventFilter(self.keyPressEater)

        # Layout para mostrar el total
        layout_total = QHBoxLayout()
        self.currencyLabel = QLabel("USD")
        layout_total.addWidget(self.currencyLabel)
        
        self.screenTotal = QLabel("TOTAL: 0.00")
        self.screenTotal.setStyleSheet("background-color: black; color: white; font-size: 16px; padding: 10px;")
        layout_total.addWidget(self.screenTotal)
        layout_total.addStretch(1)
        layout.addLayout(layout_total)

        self.setLayout(layout)
        
        # Cargar cuadrícula inicial
        self.load_search_grid()

    def load_search_grid(self):
        # Limpiar grid anterior
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        filter_text = self.busqueda_input.text().strip()
        self.cursor.execute("SELECT name, quantity, price, image_path FROM products WHERE name LIKE ?", ('%' + filter_text + '%',))
        products = self.cursor.fetchall()
        
        columns = 4
        for i, (name, qty, price, img) in enumerate(products):
            item_widget = ProductItemWidget(name, qty, price, img)
            item_widget.clicked.connect(self.add_product_from_grid)
            self.grid_layout.addWidget(item_widget, i // columns, i % columns)

    def add_product_from_grid(self, product_name):
        self.cursor.execute("SELECT name, quantity, price FROM products WHERE name = ?", (product_name,))
        product = self.cursor.fetchone()
        if product:
            name, qty, price = product
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            self.table.setItem(row_number, 0, QTableWidgetItem(name))
            self.table.setItem(row_number, 1, QTableWidgetItem("1")) # Cantidad por defecto 1
            self.table.setItem(row_number, 2, QTableWidgetItem(str(price)))
            self.calculateTotal()

    def guardar_venta(self):
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        buyer = self.cliente_actual
        seller = self.vendedor_actual
        currency = self.currencyLabel.text()
        discount = 0.0
        
        row_count = self.table.rowCount()
        if row_count == 0:
            print("No hay productos para guardar en la venta.")
            return

        # Pedir método de pago
        dialog_pago = PaymentMethodDialog(self)
        if dialog_pago.exec() != QDialog.Accepted:
            return
            
        payment_method = dialog_pago.get_method()
        status = "Pendiente" if payment_method == "Crédito" else "Pagado"

        for row in range(row_count):
            product_name = self.table.item(row, 0).text()
            quantity_sold = int(self.table.item(row, 1).text())
            self.cursor.execute("SELECT id FROM products WHERE name = ?", (product_name,))
            product_id_row = self.cursor.fetchone()
            product_id = product_id_row[0] if product_id_row else None
            
            self.cursor.execute('''INSERT INTO sales (date, buyer, seller, discount, currency, product_id, quantity, payment_method, status)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (fecha_actual, buyer, seller, discount, currency, product_id, quantity_sold, payment_method, status))

            # Restar del inventario
            if product_id:
                self.cursor.execute(
                    'UPDATE products SET quantity = quantity - ? WHERE id = ?',
                    (quantity_sold, product_id)
                )
        
        self.conexion_db.commit()
        self.load_creditos() # Actualizar lista de créditos
        
        # --- Lógica de Impresión Modular de Ticket ---
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                if settings.get("auto_print"):
                    # Preparar datos de la venta para el driver
                    items = []
                    total_venta = 0
                    for r in range(self.table.rowCount()):
                        name = self.table.item(r, 0).text()
                        qty = int(self.table.item(r, 1).text())
                        price = float(self.table.item(r, 2).text())
                        items.append({"name": name, "quantity": qty, "price": price})
                        total_venta += price * qty # OJO: Antes sumaba solo price, ahora price*qty

                    receipt_data = {
                        "date": fecha_actual,
                        "buyer": buyer,
                        "seller": seller,
                        "currency": currency,
                        "items": items,
                        "total": total_venta
                    }

                    # Obtener instancia del driver seleccionado
                    driver_name = settings.get("driver_name", "goojprt")
                    printer_name = settings.get("printer_name", "")
                    
                    printer = PrinterManager.get_printer_instance(driver_name, printer_name)
                    if printer:
                        printer.print_receipt(settings, receipt_data)
                    else:
                        print(f"Driver '{driver_name}' no encontrado.")
            except Exception as e:
                print(f"Error al intentar imprimir modularmente: {e}")

        # Limpiar
        self.table.setRowCount(0)
        self.busqueda_input.clear()
        self.calculateTotal()
        self.load_search_grid()  # Refrescar stock en la cuadrícula
        print(f"Venta guardada con éxito: {fecha_actual}")

    def abrir_busqueda_productos(self):
        dialog = ProductSearchDialog(self.cursor, self)
        if dialog.exec() == QDialog.Accepted:
            product = dialog.get_selected_data()
            if product:
                self.add_product_from_grid(product["nombre"])

    def toggle_vendedores(self):
        # Ocultar otros si están abiertos
        self.container_clientes.hide()
        self.container_monedas.hide()
        self.container_creditos.hide()
        
        if self.container_vendedores.isVisible():
            self.container_vendedores.hide()
        else:
            self.load_vendedores_inline()
            self.container_vendedores.show()
            self.search_vendedores.setFocus()

    def toggle_clientes(self):
        self.container_vendedores.hide()
        self.container_monedas.hide()
        self.container_creditos.hide()
        
        if self.container_clientes.isVisible():
            self.container_clientes.hide()
        else:
            self.load_clientes_inline()
            self.container_clientes.show()
            self.search_clientes.setFocus()

    def toggle_monedas(self):
        self.container_vendedores.hide()
        self.container_clientes.hide()
        self.container_creditos.hide()
        
        if self.container_monedas.isVisible():
            self.container_monedas.hide()
        else:
            self.load_monedas_inline()
            self.container_monedas.show()
            self.search_monedas.setFocus()

    def load_vendedores_inline(self):
        filter_text = self.search_vendedores.text()
        self.cursor.execute("SELECT name, phone, cedula FROM sellers WHERE name LIKE ? OR cedula LIKE ?", ('%' + filter_text + '%', '%' + filter_text + '%'))
        results = self.cursor.fetchall()
        self.table_vendedores.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.table_vendedores.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table_vendedores.setItem(row_number, column_number, QTableWidgetItem(str(data if data is not None else "")))

    def load_clientes_inline(self):
        filter_text = self.search_clientes.text()
        self.cursor.execute("SELECT name, phone, cedula FROM clients WHERE name LIKE ? OR cedula LIKE ?", ('%' + filter_text + '%', '%' + filter_text + '%'))
        results = self.cursor.fetchall()
        self.table_clientes.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.table_clientes.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table_clientes.setItem(row_number, column_number, QTableWidgetItem(str(data if data is not None else "")))

    def load_monedas_inline(self):
        filter_text = self.search_monedas.text()
        self.cursor.execute("SELECT name, symbol, is_crypto FROM currencies WHERE name LIKE ? OR symbol LIKE ?", ('%' + filter_text + '%', '%' + filter_text + '%'))
        results = self.cursor.fetchall()
        self.table_monedas.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.table_monedas.insertRow(row_number)
            # Columnas: Nombre, Símbolo, Tipo
            self.table_monedas.setItem(row_number, 0, QTableWidgetItem(row_data[0]))
            self.table_monedas.setItem(row_number, 1, QTableWidgetItem(row_data[1]))
            tipo = "Cripto" if row_data[2] == 1 else "Fiat"
            self.table_monedas.setItem(row_number, 2, QTableWidgetItem(tipo))

    def seleccionar_vendedor_inline(self):
        row = self.table_vendedores.currentRow()
        if row != -1:
            self.vendedor_actual = self.table_vendedores.item(row, 0).text()
            self.label_vendedor.setText(f"Vendedor: {self.vendedor_actual}")
            self.container_vendedores.hide()

    def seleccionar_cliente_inline(self):
        row = self.table_clientes.currentRow()
        if row != -1:
            self.cliente_actual = self.table_clientes.item(row, 0).text()
            self.label_cliente.setText(f"Cliente: {self.cliente_actual}")
            self.container_clientes.hide()

    def seleccionar_moneda_inline(self):
        row = self.table_monedas.currentRow()
        if row != -1:
            symbol = self.table_monedas.item(row, 1).text()
            self.currencyLabel.setText(symbol)
            self.container_monedas.hide()

    def calculateTotal(self):
        total = 0
        for row in range(self.table.rowCount()):
            cantidad_item = self.table.item(row, 1)
            precio_item = self.table.item(row, 2)
            if cantidad_item and precio_item:
                try:
                    cantidad = int(cantidad_item.text())
                    precio = float(precio_item.text())
                    total += cantidad * precio
                except ValueError:
                    pass
        self.screenTotal.setText(f"TOTAL: {total:.2f}")

    def load_creditos(self):
        self.table_creditos.setRowCount(0)
        self.cursor.execute('''SELECT s.id, s.date, s.buyer, p.name, (s.quantity * p.price), s.id 
                               FROM sales s 
                               JOIN products p ON s.product_id = p.id 
                               WHERE s.status = 'Pendiente' 
                               ORDER BY s.date DESC''')
        creditos = self.cursor.fetchall()
        
        for row_number, row_data in enumerate(creditos):
            self.table_creditos.insertRow(row_number)
            for column_number, data in enumerate(row_data[:-1]):
                self.table_creditos.setItem(row_number, column_number, QTableWidgetItem(str(data)))
            
            # Botones de Acción
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            pay_btn = QPushButton("Pagado")
            pay_btn.setStyleSheet("background-color: #2ecc71; color: white; border-radius: 4px;")
            pay_btn.clicked.connect(lambda *args, sid=row_data[0]: self.marcar_como_pagado(sid))
            
            reject_btn = QPushButton("Rechazar")
            reject_btn.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 4px;")
            reject_btn.clicked.connect(lambda *args, sid=row_data[0]: self.rechazar_venta(sid))
            
            actions_layout.addWidget(pay_btn)
            actions_layout.addWidget(reject_btn)
            self.table_creditos.setCellWidget(row_number, 5, actions_widget)

    def toggle_creditos(self):
        if self.container_creditos.isVisible():
            self.container_creditos.hide()
        else:
            self.load_creditos()
            self.container_creditos.show()

    def marcar_como_pagado(self, sale_id):
        self.cursor.execute("UPDATE sales SET status = 'Pagado' WHERE id = ?", (sale_id,))
        self.conexion_db.commit()
        self.load_creditos()
        print(f"Crédito {sale_id} marcado como Pagado.")

    def rechazar_venta(self, sale_id):
        # Obtener datos de la venta para devolver al inventario
        self.cursor.execute("SELECT product_id, quantity FROM sales WHERE id = ?", (sale_id,))
        res = self.cursor.fetchone()
        if res:
            product_id, quantity = res
            # Actualizar estado y devolver stock
            self.cursor.execute("UPDATE sales SET status = 'Rechazado' WHERE id = ?", (sale_id,))
            if product_id:
                self.cursor.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (quantity, product_id))
            self.conexion_db.commit()
            self.load_creditos()
            self.load_search_grid() # Refrescar grid de productos
            print(f"Venta {sale_id} rechazada. Stock devuelto al inventario.")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SalesTab()
    window.show()
    sys.exit(app.exec())
