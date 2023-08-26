import sys
import csv
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget
from PySide2.QtGui import QPixmap
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
        self.resize(600, 400)

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

        # Crear botón para exportar los datos vendidos a un archivo CSV
        export_button = QPushButton('Exportar a CSV')
        export_button.clicked.connect(self.export_to_csv)
        layout.addWidget(export_button)

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
                    scaled_pixmap = pixmap.scaled(100, 100)  # Escalar la imagen para que quepa en la celda
                    image_label.setPixmap(scaled_pixmap)
                    #image_label.setFixedSize(222, 222)
                    #self.table.setColumnWidth(1, 200)
                    #image_label.setScaledContents(True)
                    #image_label.setAlignment(alignCenter)
                    self.table.setCellWidget(row_number, column_number, image_label)
                else:
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def select_image(self):
        # Abrir la ventana de búsqueda de archivos para seleccionar la imagen
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Seleccionar Imagen', '', 'Image Files (*.png *.jpg *.jpeg)')

        if file_path:
            # Mostrar la ruta de la imagen en el campo de entrada
            self.image_path_input.setText(file_path)

    def add_product(self):
        # Obtener los valores de los campos de entrada
        name = self.name_input.text()
        quantity = int(self.quantity_input.text())
        price = float(self.price_input.text())
        image_path = self.image_path_input.text()

        # Insertar el producto en la base de datos
        cursor.execute('INSERT INTO products (name, quantity, price, image_path) VALUES (?, ?, ?, ?)',
                       (name, quantity, price, image_path))
        connection.commit()

        # Limpiar los campos de entrada
        self.name_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.image_path_input.clear()

        # Recargar los productos en la tabla
        self.load_products()

    def export_to_csv(self):
        # Obtener la ruta de archivo para guardar el archivo CSV
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, 'Guardar como CSV', '', 'CSV Files (*.csv)')

        if file_path:
            # Obtener los productos vendidos
            cursor.execute('SELECT * FROM products')
            products = cursor.fetchall()

            # Escribir los productos en el archivo CSV
            with open(file_path, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['ID', 'Nombre', 'Cantidad', 'Precio', 'Ruta de la Imagen'])
                writer.writerows(products)

            # Mostrar un mensaje de éxito
            print('Datos exportados correctamente.')


# Inicializar la aplicación de PySide
app = QApplication(sys.argv)

# Crear la ventana principal
window = MainWindow()
window.show()

# Ejecutar la aplicación
sys.exit(app.exec_())
