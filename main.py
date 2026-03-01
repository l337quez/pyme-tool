import sys
import csv
import os
import importlib.util
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QIcon
import sqlite3
from sale import SalesTab
from inventory import InventoryTab
from product import ProductsTab
from home import HomeTab
from report import ReportsTab
from about import AboutTab
from settings import SettingsTab
from plugins_tab import PluginsTab
import plugin_config as cfg

# ...

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Aplicación de Inventario')
        self.resize(1000, 650) 
        self.setMinimumSize(900, 600)

        # Create the tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create the tabs
        self.home_tab = HomeTab()
        self.inventory_tab = InventoryTab()
        self.product_tab = ProductsTab()
        self.sale_tab = SalesTab()
        self.report_tab = ReportsTab()
        self.about_tab = AboutTab()
        self.settings_tab = SettingsTab()

        # Connect navigation signal from HomeTab (now emits tab name instead of index)
        self.home_tab.navigate_to.connect(self.navigate_by_name)

        # Add the core tabs (Configuración and About will be added after plugins)
        self.tab_widget.addTab(self.home_tab,      'Home')         
        self.tab_widget.addTab(self.inventory_tab,  'Inventario') 
        self.tab_widget.addTab(self.product_tab,    'Productos')   
        self.tab_widget.addTab(self.sale_tab,        'Ventas')        
        self.tab_widget.addTab(self.report_tab,      'Reportes')     

        # Record how many core tabs there are (so we know where plugins start)
        self._core_tab_count = self.tab_widget.count()

        # Cargar plugins dinámicamente desde la carpeta plugins/
        self._plugin_instances = []  # lista de (plugin_instance, tab_index)
        self.load_plugins()

        # Plugin Manager tab
        self.plugins_manager_tab = PluginsTab(reload_callback=self.reload_plugins)
        self.tab_widget.addTab(self.plugins_manager_tab, '🔌 Plugins')

        # Configuración tab (before About)
        self.tab_widget.addTab(self.settings_tab, 'Configuración') 

        # About tab (always last)
        self.tab_widget.addTab(self.about_tab, 'About')        

        # Refresh SalesTab when selected
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def navigate_by_name(self, name: str):
        """Changes the current tab by finding a tab with the matching name."""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == name:
                self.tab_widget.setCurrentIndex(i)
                return


    def reload_plugins(self):
        """
        Elimina TODOS los tabs de plugins actuales del TabWidget,
        limpia los cards del Home, y recarga desde 0 los plugins habilitados.
        Llamado por el botón Refresh del Plugin Manager.
        """
        # 1. Deactivar hooks de plugins que se van a quitar
        for plugin, _ in self._plugin_instances:
            plugin.on_deactivated()

        # 2. Quitar las pestañas de plugins del TabWidget.
        #    Empezamos desde el final para no alterar los índices mientras quitamos.
        #    Los plugins están entre _core_tab_count y (count - 2: Plugins Manager, About)
        plugin_tab_indices = sorted(
            [idx for _, idx in self._plugin_instances], reverse=True
        )
        for idx in plugin_tab_indices:
            self.tab_widget.removeTab(idx)

        self._plugin_instances = []

        # 3. Limpiar cards del Home
        self.home_tab.clear_plugin_cards()

        # 4. Recargar plugins habilitados
        self.load_plugins()

        # 5. Actualizar los índices del Plugin Manager, Config y About
        plugins_mgr_idx = self.tab_widget.indexOf(self.plugins_manager_tab)
        config_idx      = self.tab_widget.indexOf(self.settings_tab)
        about_idx       = self.tab_widget.indexOf(self.about_tab)
        print(f"[Plugins] Recargado. Plugins mgr: #{plugins_mgr_idx} Config: #{config_idx} About: #{about_idx}")

    def load_plugins(self):
        """
        Escanea la carpeta `plugins/` y carga solo los plugins habilitados.
        Las pestañas se insertan ANTES de la pestaña del Plugin Manager.
        """
        plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
        if not os.path.isdir(plugins_dir):
            return

        # Insertar justo antes de las pestañas 'Plugins' y 'About'
        # Encontrar el índice de inserción (antes de la pestaña 🔌 Plugins si ya existe)
        mgr_idx = self.tab_widget.indexOf(self.plugins_manager_tab) \
            if hasattr(self, 'plugins_manager_tab') else self.tab_widget.count()

        insert_before = mgr_idx if mgr_idx >= 0 else self.tab_widget.count()

        for folder in sorted(os.listdir(plugins_dir)):
            plugin_path = os.path.join(plugins_dir, folder, "plugin.py")
            if not os.path.isfile(plugin_path):
                continue

            if not cfg.is_enabled(folder):
                print(f"[Plugins] Omitido (deshabilitado): '{folder}'")
                continue

            try:
                spec = importlib.util.spec_from_file_location(
                    f"plugins.{folder}.plugin", plugin_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                plugin_cls = getattr(module, "Plugin")
                plugin = plugin_cls()

                widget = plugin.create_widget()
                # Insertamos en la posición correcta
                self.tab_widget.insertTab(insert_before, widget, plugin.tab_label)
                plugin_tab_index = insert_before
                insert_before += 1  # próximo plugin va después

                self._plugin_instances.append((plugin, plugin_tab_index))

                if plugin.show_in_home:
                    plugin_folder = os.path.join(plugins_dir, folder)
                    default_icon  = os.path.join(plugin_folder, plugin.icon)
                    icon_path = cfg.get_icon(folder, default_icon)
                    idx = plugin_tab_index
                    self.home_tab.add_plugin_card(
                        plugin.name,
                        icon_path,
                        lambda checked=False, i=idx: self.tab_widget.setCurrentIndex(i)
                    )

                print(f"[Plugins] Cargado: '{plugin.name}' (pestaña #{plugin_tab_index})")

            except Exception as e:
                print(f"[Plugins] Error al cargar '{folder}': {e}")


    def on_tab_changed(self, index):
        if self.tab_widget.tabText(index) == 'Ventas':
            self.sale_tab.load_search_grid()

        # Llamar hooks de activación/desactivación en plugins
        for plugin, plugin_idx in self._plugin_instances:
            if index == plugin_idx:
                plugin.on_activated()
            else:
                plugin.on_deactivated()

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
sys.exit(app.exec())
