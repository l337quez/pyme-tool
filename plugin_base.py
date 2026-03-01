"""
plugin_base.py
==============
Contrato base que todo plugin de Pyme Tool debe seguir.

Para crear un plugin:
1. Crea una carpeta dentro de `plugins/` con el nombre de tu plugin.
2. Dentro de esa carpeta, crea un archivo `plugin.py`.
3. En `plugin.py`, define una clase llamada `Plugin` que herede de `BasePlugin`.
4. Implementa el método `create_widget()` que retorna un QWidget con la UI de tu plugin.
5. (Opcional) Crea un `plugin.json` con metadatos:
       {
         "author": "Tu nombre",
         "version": "1.0.0",
         "description": "Descripción breve del plugin."
       }

Ejemplo mínimo (plugins/mi_plugin/plugin.py):
---------------------------------------------
    from plugin_base import BasePlugin
    from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

    class Plugin(BasePlugin):
        name = "Mi Plugin"           # Nombre del card en Home
        icon = "icon.png"            # Ruta relativa a la carpeta del plugin
        show_in_home = True          # True = aparece como card en el Home
        tab_label = "Mi Plugin"      # Nombre en la pestaña del TabWidget

        def create_widget(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(QLabel("¡Hola desde mi plugin!"))
            return widget
"""

from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget


class BasePlugin(ABC):
    """
    Clase base abstracta para todos los plugins de Pyme Tool.

    Atributos de clase (override en tu subclase):
        name (str):           Nombre visible del plugin (card en Home y pestaña).
        icon (str):           Ruta al ícono PNG relativa a la carpeta del plugin.
                              Si no existe o está vacío, se muestra un ícono genérico.
        show_in_home (bool):  Si True, aparece como acceso directo en el Home.
        tab_label (str):      Etiqueta de la pestaña en el TabWidget.
    """

    # --- Metadatos del plugin (el desarrollador los sobreescribe) ---
    name: str = "Plugin sin nombre"
    icon: str = "icon.png"
    show_in_home: bool = True
    tab_label: str = "Plugin"

    # --- Método obligatorio ---
    @abstractmethod
    def create_widget(self) -> QWidget:
        """
        Crea y retorna el widget principal de este plugin.
        Este widget se mostrará dentro de la pestaña del TabWidget.
        """
        ...

    # --- Métodos opcionales (hooks) ---
    def on_activated(self) -> None:
        """
        Llamado cada vez que el usuario navega a la pestaña de este plugin.
        Úsalo para refrescar datos, detener/arrancar timers, etc.
        """
        pass

    def on_deactivated(self) -> None:
        """
        Llamado cada vez que el usuario sale de la pestaña de este plugin.
        """
        pass
