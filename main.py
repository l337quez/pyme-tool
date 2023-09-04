import sys
import csv
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QIcon
import sqlite3
from sale import SalesTab
from inventory import InventoryTab

# ...

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Aplicación de Inventario')
        self.resize(600, 400)

        # Create the tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create the tabs
        self.home_tab = QWidget()
        self.inventory_tab = InventoryTab()
        self.sale_tab = SalesTab()

        # Add the tabs to the tab widget
        self.tab_widget.addTab(self.home_tab, 'Home')
        self.tab_widget.addTab(self.inventory_tab, 'Inventario')
        self.tab_widget.addTab(self.sale_tab, 'Ventas')

        # ...
        # Set the icon
        app.setWindowIcon(QIcon('assets/pyme-tools-logo.png'))

    # ...

# ...

# Inicializar la aplicación de PySide
app = QApplication(sys.argv)

# Crear la ventana principal
window = MainWindow()
window.show()

# Ejecutar la aplicación
sys.exit(app.exec_())
