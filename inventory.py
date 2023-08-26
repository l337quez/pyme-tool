import sys
import csv
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget, QHBoxLayout
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt
import sqlite3

# Crear la conexión a la base de datos SQLite
connection = sqlite3.connect('inventory.db')
cursor = connection.cursor()

# Crear la tabla de productos si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS products
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, quantity INTEGER, price REAL, image_path TEXT)''')
connection.commit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Aplicación de Inventario')
        self.resize(800, 400)

        # Crear el widget de pestañas
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Crear las pestañas
        self.home_tab = QWidget()
        self.inventory_tab = InventoryTab()
        self.accounting_tab = QWidget()

        # Agregar las pestañas al widget de pestañas
        self.tab_widget.addTab(self.home_tab, 'Home')
        self.tab_widget.addTab(self.inventory_tab, 'Inventario')
        self.tab_widget.addTab(self.accounting_tab, 'Contabilidad')


class InventoryTab(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # Layout para los elementos de entrada y botones
        input_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)

        # Crear campos de entrada de datos
        name_label = QLabel('Nombre del Producto:')
        self.name_input = QLineEdit()
        quantity_label = QLabel('Cantidad:')
        self.quantity_input = QLineEdit()
        price_label = QLabel('Precio:')
        self.price_input = QLineEdit()
        image_label = QLabel('Imagen:')
        self.image_path_input = QLineEdit()
        self.image_path_input.setReadOnly(True)

        input_layout.addWidget(name_label)
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(quantity_label)
        input_layout.addWidget(self.quantity_input)
        input_layout.addWidget(price_label)
        input_layout.addWidget(self.price_input)
        input_layout.addWidget(image_label)
        input_layout.addWidget(self.image_path_input)

        # Botones de selección de imagen y agregar producto
        button_layout = QHBoxLayout()
        input_layout.addLayout(button_layout)

        select_image_button = QPushButton('Seleccionar Imagen')
        select_image_button.clicked.connect(self.select_image)
        add_button = QPushButton('Agregar Producto')
        add_button.clicked.connect(self.add_product)

        button_layout.addWidget(select_image_button)
        button_layout.addWidget(add_button)

        # Layout para la visualización de la imagen seleccionada
        #image_layout = QHBoxLayout()
        #main_layout.addLayout(input_layout)
        #main_layout.addStretch(1)  # Agregar un stretch para que la tabla ocupe todo el espacio vertical disponible

        self.selected_image_label = QLabel()
        self.selected_image_label.setFixedSize(200, 200)
        self.selected_image_label.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.selected_image_label)

        # Crear tabla para mostrar los productos vendidos
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Añadir una columna adicional para la imagen
        self.table.setHorizontalHeaderLabels(['ID', 'Nombre', 'Cantidad', 'Precio', 'Imagen'])

        # Ajustar el tamaño de las columnas para que ocupen todo el espacio horizontal
        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addWidget(self.table)

        # Cargar los productos vendidos en la tabla
        self.load_products()

        # Conectar la señal de celda clickeada
        self.table.cellClicked.connect(self.show_selected_image)

    def load_products(self):
        # Limpiar la tabla
        self.table.setRowCount(0)

        # Obtener los productos vendidos de la base de datos
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()

        # Agregar los productos a la tabla
        for row_number, row_data in enumerate(products):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):

                item = QTableWidgetItem(str(data))
                self.table.setItem(row_number, column_number, item)

    def select_image(self):
        # Abrir el diálogo para seleccionde archivo y obtener la ruta de la imagen seleccionada
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter('Imágenes (*.png *.jpg *.jpeg)')
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            image_path = selected_files[0]
            self.image_path_input.setText(image_path)

    def add_product(self):
        # Obtener los datos del formulario
        name = self.name_input.text()
        quantity = self.quantity_input.text()
        price = self.price_input.text()
        image_path = self.image_path_input.text()

        # Insertar el producto en la base de datos
        cursor.execute('INSERT INTO products (name, quantity, price, image_path) VALUES (?, ?, ?, ?)',
                       (name, quantity, price, image_path))
        connection.commit()

        # Limpiar los campos de entrada de datos
        self.name_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.image_path_input.clear()

        # Actualizar la tabla de productos vendidos
        self.load_products()

    def show_selected_image(self, row, column):
        # Obtener la ruta de la imagen de la celda seleccionada
        image_path = self.table.item(row, 4).text()

        # Mostrar la imagen en el QLabel
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.selected_image_label.setPixmap(scaled_pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
