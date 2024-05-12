import sqlite3
from PySide2.QtWidgets import (QVBoxLayout, QLabel, QLineEdit, QCompleter, QWidget, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QApplication )
from PySide2.QtCore import (Qt, QObject, QEvent)

class KeyPressEater(QObject):
    def __init__(self, parent=None):
        super(KeyPressEater, self).__init__(parent)
        self.parent = parent

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:
            if isinstance(obj, QTableWidget):
                current_index = obj.currentRow()
                if current_index != -1:
                    obj.removeRow(current_index)
                    if self.parent:
                        self.parent.calculateTotal()
                    return True
        return False


class SalesTab(QWidget):
    def __init__(self):
        super().__init__()

        # Configuración del layout principal
        layout = QVBoxLayout()

        # Botones principales en la parte superior
        lh_main = QHBoxLayout()
        buttons = [
            QPushButton('Vendedores (F2)'), QPushButton('Clientes (F3)'),
            QPushButton('Monedas (F4)'), QPushButton('Buscar Productos (F5)')
        ]
        for button in buttons:
            lh_main.addWidget(button)
            button.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addLayout(lh_main)

        # Sección de búsqueda y agregación de productos
        layout_horizontal = QHBoxLayout()
        self.busqueda_input = QLineEdit()
        self.busqueda_input.setPlaceholderText("Ingrese el nombre del producto")
        self.busqueda_input.textChanged.connect(self.mostrar_recomendaciones)
        layout_horizontal.addWidget(self.busqueda_input)

        self.addProductBtn = QPushButton('Agregar producto')
        self.addProductBtn.clicked.connect(self.addProduct)
        layout_horizontal.addWidget(self.addProductBtn)

        self.sellerName = QLineEdit()
        self.sellerName.setPlaceholderText("Nombre del vendedor")
        layout_horizontal.addWidget(self.sellerName)
        layout.addLayout(layout_horizontal)

        # Configuración de la tabla para mostrar los productos
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Nombre', 'Cantidad', 'Precio'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)

        # Eliminar filas
        self.keyPressEater = KeyPressEater(self)
        self.table.installEventFilter(self.keyPressEater)

        # Layout para mostrar el total, asegurando que está en el fondo
        layout_total = QHBoxLayout()
        self.screenTotal = QLabel("TOTAL: 0.00")
        self.screenTotal.setStyleSheet("background-color: black; color: white; font-size: 16px; padding: 10px;")
        layout_total.addWidget(self.screenTotal)
        layout_total.addStretch(1)
        layout.addLayout(layout_total)

        self.setLayout(layout)

        # Conexión a la base de datos
        self.conexion_db = sqlite3.connect('inventory.db')
        self.cursor = self.conexion_db.cursor()

    def mostrar_recomendaciones(self):
        texto_busqueda = self.busqueda_input.text()
        self.cursor.execute("SELECT name FROM products WHERE name LIKE ?", ('%' + texto_busqueda + '%',))
        productos = self.cursor.fetchall()
        if productos:
            completer = QCompleter([producto[0] for producto in productos])
            self.busqueda_input.setCompleter(completer)

    def addProduct(self):
        productName = self.busqueda_input.text().strip()
        if productName:
            self.cursor.execute("SELECT name, quantity, price FROM products WHERE name = ?", (productName,))
            productos = self.cursor.fetchall()

            for row_data in productos:
                row_number = self.table.rowCount()
                self.table.insertRow(row_number)  # Inserta una nueva fila en la tabla
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.table.setItem(row_number, column_number, item)

            self.calculateTotal()  # Calcula el total cada vez que se añade un producto nuevo


    def calculateTotal(self):
        total = 0
        for row in range(self.table.rowCount()):
            cantidad = int(self.table.item(row, 1).text())
            precio = float(self.table.item(row, 2).text())
            total += cantidad * precio
        self.screenTotal.setText(f"TOTAL: {total:.2f}")



# Para correr la aplicación
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SalesTab()
    window.show()
    sys.exit(app.exec_())
