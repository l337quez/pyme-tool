import sys
import csv
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget
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
        self.inventory_tab = QWidget()
        self.accounting_tab = QWidget()

        # Agregar las pestañas al widget de pestañas
        self.tab_widget.addTab(self.home_tab, 'Home')
        self.tab_widget.addTab(self.inventory_tab, 'Inventario')
        self.tab_widget.addTab(self.accounting_tab, 'Contabilidad')

        # Configurar el contenido de cada pestaña
        self.setup_home_tab()
        self.setup_inventory_tab()
        self.setup_accounting_tab()

    def setup_home_tab(self):
        layout = QVBoxLayout()
        label = QLabel('Esta es la pestaña Home')
        layout.addWidget(label)
        self.home_tab.setLayout(layout)

    def setup_inventory_tab(self):
        layout = QVBoxLayout()

        # Crear campos de entrada de datos
        self.name_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.price_input = QLineEdit()

        layout.addWidget(QLabel('Nombre del Producto:'))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel('Cantidad:'))
        layout.addWidget(self.quantity_input)

        layout.addWidget(QLabel('Precio:'))
        layout.addWidget(self.price_input)

        # Crear botón para seleccionar la imagen
        self.image_path_input = QLineEdit()
        self.image_path_input.setReadOnly(True)
        layout.addWidget(QLabel('Imagen:'))
        layout.addWidget(self.image_path_input)

        select_image_button = QPushButton('Seleccionar Imagen')
        select_image_button.clicked.connect(self.select_image)
        layout.addWidget(select_image_button)

        # Crear botón para agregar productos
        add_button = QPushButton('Agregar Producto')
        add_button.clicked.connect(self.add_product)
        layout.addWidget(add_button)

        # Crear tabla para mostrar los productos vendidos
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Añadir una columna adicional para la imagen
        self.table.setHorizontalHeaderLabels(['ID', 'Nombre', 'Cantidad', 'Precio', 'Imagen'])
        layout.addWidget(self.table)

        # Crear QLabel para mostrar la imagen de la fila seleccionada
        self.selected_image_label = QLabel()
        self.selected_image_label.setFixedSize(200, 200)
        self.selected_image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selected_image_label)

        self.table.cellClicked.connect(self.show_selected_image)

        self.inventory_tab.setLayout(layout)

        # Cargar los productos vendidos en la tabla
        self.load_products()

    def setup_accounting_tab(self):
        layout = QVBoxLayout()
        label = QLabel('Esta es la pestaña Contabilidad')
        layout.addWidget(label)
        self.accounting_tab.setLayout(layout)

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
                if column_number == 4:  # La columna 4 contiene la ruta de la imagen
                    # Crear un QLabel y mostrar la imagen
                    image_label = QLabel()
                    pixmap = QPixmap(data)  # Cargar la imagen desde la ruta
                    scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)  # Escalar la imagen para que quepa en la celda
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setFixedSize(100, 100)  # Establecer el tamaño fijo del QLabel para mostrar la imagen
                    image_label.setAlignment(Qt.AlignCenter)
                    self.table.setCellWidget(row_number, column_number, image_label)
                else:
                    item = QTableWidgetItem(str(data))
                    self.table.setItem(row_number, column_number, item)

    def select_image(self):
        # Abrir el diálogo para seleccionar un archivo de imagen
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Images (*.png *.xpm *.jpg *.bmp)')
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            file_path = selected_files[0]
            self.image_path_input.setText(file_path)

    def add_product(self):
        # Obtener los datos ingresados por el usuario
        name = self.name_input.text()
        quantity = self.quantity_input.text()
        price = self.price_input.text()
        image_path = self.image_path_input.text()

        # Insertar los datos en la base de datos
        cursor.execute('INSERT INTO products (name, quantity, price, image_path) VALUES (?, ?, ?, ?)', (name, quantity, price, image_path))
        connection.commit()

        # Limpiar los campos de entrada de datos
        self.name_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.image_path_input.clear()

        # Actualizar la tabla
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
