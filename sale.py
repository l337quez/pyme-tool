import sqlite3
from PySide2.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QCompleter, QWidget, QHBoxLayout

class SalesTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Crear el layout horizontal para el cuadro de búsqueda y la pantalla negra
        layout_horizontal = QHBoxLayout()

        # Crear la entrada de búsqueda de productos
        self.busqueda_input = QLineEdit()
        self.busqueda_input.setPlaceholderText("Ingrese el nombre del producto")
        self.busqueda_input.textChanged.connect(self.mostrar_recomendaciones)
        layout_horizontal.addWidget(self.busqueda_input)

        # Crear la pantalla de la calculadora
        self.pantalla = QLabel()
        self.pantalla.setStyleSheet("background-color: black; color: white;")
        layout_horizontal.addWidget(self.pantalla)

        # Agregar el layout horizontal al layout principal
        layout.addLayout(layout_horizontal)

        # Crear el layout horizontal para el resultado de la búsqueda y el input de operaciones
        layout_horizontal2 = QHBoxLayout()

        # Crear el label para mostrar el producto encontrado
        self.producto_encontrado = QLabel()
        layout_horizontal2.addWidget(self.producto_encontrado)

        # Crear la entrada de texto para las operaciones matemáticas
        self.entrada = QLineEdit()
        self.entrada.returnPressed.connect(self.calcular)
        layout_horizontal2.addWidget(self.entrada)

        # Agregar el layout horizontal al layout principal
        layout.addLayout(layout_horizontal2)

        self.setLayout(layout)

        # Conectar a la base de datos SQLite
        self.conexion_db = sqlite3.connect('inventory.db')
        self.cursor = self.conexion_db.cursor()

    def mostrar_recomendaciones(self):
        texto_busqueda = self.busqueda_input.text()
        self.cursor.execute("SELECT name FROM products WHERE name LIKE ?", (f"%{texto_busqueda}%",))
        producto = self.cursor.fetchone()

        if producto:
            self.producto_encontrado.setText(f"Producto encontrado: {producto[0]}")
        else:
            self.producto_encontrado.setText("")

    def calcular(self):
        expresion = self.entrada.text()
        resultado = eval(expresion.replace('/', '').replace('*', '').replace('+', '').replace('-', ''))
        self.pantalla.setText(str(resultado))
