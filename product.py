import sqlite3
import json
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, 
                             QHeaderView, QAbstractItemView, QMessageBox, QGridLayout)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from printers.manager import PrinterManager

class ProductsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_path = 'settings.json'

        # Conexión a la base de datos
        self.conexion_db = sqlite3.connect('pyme_tool_data_base.db')
        self.cursor = self.conexion_db.cursor()

        # Layout principal
        layout = QHBoxLayout(self)

        # Panel Izquierdo: Formulario
        form_panel = QWidget()
        form_layout = QVBoxLayout(form_panel)
        form_panel.setFixedWidth(300)

        title_label = QLabel("Gestión de Producto")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        form_layout.addWidget(title_label)

        # Campos de entrada
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID (Solo lectura)")
        self.id_input.setReadOnly(True)
        form_layout.addWidget(QLabel("ID:"))
        form_layout.addWidget(self.id_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del producto")
        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.name_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Cantidad en stock")
        form_layout.addWidget(QLabel("Cantidad:"))
        form_layout.addWidget(self.quantity_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Precio unitario")
        form_layout.addWidget(QLabel("Precio:"))
        form_layout.addWidget(self.price_input)

        self.image_path_input = QLineEdit()
        self.image_path_input.setPlaceholderText("Ruta de la imagen")
        form_layout.addWidget(QLabel("Imagen:"))
        
        image_h_layout = QHBoxLayout()
        image_h_layout.addWidget(self.image_path_input)
        self.btn_browse_image = QPushButton("...")
        self.btn_browse_image.setFixedWidth(30)
        self.btn_browse_image.clicked.connect(self.seleccionar_imagen)
        image_h_layout.addWidget(self.btn_browse_image)
        form_layout.addLayout(image_h_layout)

        # Vista previa de imagen
        self.image_preview = QLabel("Sin imagen")
        self.image_preview.setFixedSize(150, 150)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        form_layout.addWidget(self.image_preview, alignment=Qt.AlignCenter)

        # Botones de Acción
        btn_layout = QGridLayout()
        self.btn_add = QPushButton("Añadir")
        self.btn_add.clicked.connect(self.agregar_producto)
        self.btn_update = QPushButton("Actualizar")
        self.btn_update.clicked.connect(self.actualizar_producto)
        self.btn_delete = QPushButton("Eliminar")
        self.btn_delete.clicked.connect(self.eliminar_producto)
        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.clicked.connect(self.limpiar_formulario)
        
        self.btn_print_label = QPushButton("🖨️ Imprimir Etiqueta")
        self.btn_print_label.setStyleSheet("background-color: #34495e; color: white; font-weight: bold; padding: 5px;")
        self.btn_print_label.clicked.connect(self.imprimir_etiqueta)

        btn_layout.addWidget(self.btn_add, 0, 0)
        btn_layout.addWidget(self.btn_update, 0, 1)
        btn_layout.addWidget(self.btn_delete, 1, 0)
        btn_layout.addWidget(self.btn_clear, 1, 1)
        btn_layout.addWidget(self.btn_print_label, 2, 0, 1, 2)
        form_layout.addLayout(btn_layout)

        form_layout.addStretch()

        # Panel Derecho: Tabla
        table_panel = QWidget()
        table_layout = QVBoxLayout(table_panel)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Stock", "Precio"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.cargar_seleccion)
        table_layout.addWidget(self.table)

        layout.addWidget(form_panel)
        layout.addWidget(table_panel)

        self.cargar_datos()

    def imprimir_etiqueta(self):
        id_p = self.id_input.text()
        if not id_p:
            QMessageBox.warning(self, "Sin selección", "Por favor selecciona un producto para imprimir su etiqueta.")
            return

        # Cargar configuración de impresora
        if not os.path.exists(self.settings_path):
            QMessageBox.warning(self, "Configuración faltante", "Por favor configura la impresora en la pestaña de Configuración primero.")
            return

        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            driver_name = settings.get("driver_name", "goojprt")
            printer_name = settings.get("printer_name", "")
            
            product_data = {
                "id": id_p,
                "name": self.name_input.text(),
                "price": float(self.price_input.text() if self.price_input.text() else 0)
            }

            printer = PrinterManager.get_printer_instance(driver_name, printer_name)
            if printer:
                printer.print_label(product_data)
                QMessageBox.information(self, "Impresión", f"Etiqueta enviada a {printer_name if printer_name else 'la impresora'}.")
            else:
                QMessageBox.critical(self, "Error", f"Driver '{driver_name}' no encontrado.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo imprimir: {str(e)}")

    def cargar_datos(self):
        self.table.setRowCount(0)
        self.cursor.execute("SELECT id, name, quantity, price FROM products")
        products = self.cursor.fetchall()
        for row, data in enumerate(products):
            self.table.insertRow(row)
            for col, value in enumerate(data):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def cargar_seleccion(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        id_prod = self.table.item(row, 0).text()
        
        self.cursor.execute("SELECT id, name, quantity, price, image_path FROM products WHERE id = ?", (id_prod,))
        result = self.cursor.fetchone()
        
        if result:
            id_p, name, qty, price, img_path = result
            self.id_input.setText(str(id_p))
            self.name_input.setText(name)
            self.quantity_input.setText(str(qty))
            self.price_input.setText(str(price))
            self.image_path_input.setText(img_path if img_path else "")
            self.mostrar_imagen(img_path)

    def mostrar_imagen(self, path):
        if path:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.image_preview.setPixmap(pixmap.scaled(self.image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        self.image_preview.setText("Sin imagen")
        self.image_preview.setPixmap(QPixmap())

    def seleccionar_imagen(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        if path:
            self.image_path_input.setText(path)
            self.mostrar_imagen(path)

    def limpiar_formulario(self):
        self.id_input.clear()
        self.name_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.image_path_input.clear()
        self.image_preview.setText("Sin imagen")
        self.image_preview.setPixmap(QPixmap())
        self.table.clearSelection()

    def agregar_producto(self):
        name = self.name_input.text()
        qty = self.quantity_input.text()
        price = self.price_input.text()
        img = self.image_path_input.text()

        if not name or not qty or not price:
            QMessageBox.warning(self, "Campos incompletos", "Por favor completa los campos principales.")
            return

        try:
            self.cursor.execute("INSERT INTO products (name, quantity, price, image_path) VALUES (?, ?, ?, ?)",
                               (name, int(qty), float(price), img))
            self.conexion_db.commit()
            self.cargar_datos()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Producto añadido correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo añadir el producto: {str(e)}")

    def actualizar_producto(self):
        id_p = self.id_input.text()
        if not id_p:
            QMessageBox.warning(self, "Sin selección", "Por favor selecciona un producto de la tabla.")
            return

        name = self.name_input.text()
        qty = self.quantity_input.text()
        price = self.price_input.text()
        img = self.image_path_input.text()

        try:
            self.cursor.execute("UPDATE products SET name=?, quantity=?, price=?, image_path=? WHERE id=?",
                               (name, int(qty), float(price), img, id_p))
            self.conexion_db.commit()
            self.cargar_datos()
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el producto: {str(e)}")

    def eliminar_producto(self):
        id_p = self.id_input.text()
        if not id_p:
            QMessageBox.warning(self, "Sin selección", "Por favor selecciona un producto de la tabla.")
            return

        reply = QMessageBox.question(self, "Confirmar eliminación", "¿Estás seguro de que deseas eliminar este producto?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM products WHERE id=?", (id_p,))
                self.conexion_db.commit()
                self.cargar_datos()
                self.limpiar_formulario()
                QMessageBox.information(self, "Éxito", "Producto eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto: {str(e)}")
