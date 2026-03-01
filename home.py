from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QLayout, QSizePolicy)
from PySide6.QtGui import QPixmap, QCursor
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QSize

class FlowLayout(QLayout):
    """
    Standard Qt FlowLayout (wrapping layout).
    Adapts content to the available width by moving items to the next line.
    """
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins()
        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        margin, _, _, _ = self.getContentsMargins()

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


class CardWidget(QFrame):
    clicked = Signal()

    def __init__(self, title, image_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 240)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setObjectName("Card")
        
        # Estilos para el efecto hover y diseño PREMIUM
        self.setStyleSheet("""
            #Card {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 15px;
            }
            #Card:hover {
                border: 2px solid #3498db;
                background-color: #f8faff;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Imagen
        self.image_label = QLabel()
        self.image_label.setFixedSize(140, 140)
        self.image_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.image_label.setText("Imagen no encontrada")
            self.image_label.setStyleSheet("color: #999; font-style: italic;")
        
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # Título
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.title_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class HomeTab(QWidget):
    navigate_to = Signal(str)   # emite el nombre del tab
    open_plugin = Signal(str)   # emite el nombre del plugin a abrir

    def __init__(self):
        super().__init__()

        # Layout principal que contendrá el ScrollArea
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0,0,0,0)

        # ScrollArea para manejar pantallas pequeñas y responsividad vertical
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Desactivar scroll horizontal
        self.scroll_area.setStyleSheet("background: transparent;")
        
        # Contenedor para el contenido real del Home
        self.container = QWidget()
        self.container.setObjectName("HomeContainer")
        self.container.setStyleSheet("#HomeContainer { background: #f5f6fa; }")
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Título Superior
        header_label = QLabel("Panel de Control")
        header_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(header_label, alignment=Qt.AlignLeft)

        # Contenedor para las cards usando FlowLayout (¡RESPONSIVO!)
        self.cards_container = QWidget()
        self.cards_layout = FlowLayout(self.cards_container, spacing=20)
        
        # Definición de las cards (Título, Imagen, Nombre exacto del Tab)
        card_data = [
            ("Inventario", "assets/cards/inventory.png", "Inventario"),
            ("Productos", "assets/cards/product.png", "Productos"),
            ("Ventas", "assets/cards/sale.png", "Ventas"),
            ("Reportes", "assets/cards/dashboard.png", "Reportes"),
            ("Plugins", "assets/cards/plugin.png", "🔌 Plugins"),
            ("Configuración", "assets/cards/settings.png", "Configuración")
        ]

        for title, img, tab_name in card_data:
            card = CardWidget(title, img)
            card.clicked.connect(lambda t=tab_name: self.navigate_to.emit(t))
            self.cards_layout.addWidget(card)

        main_layout.addWidget(self.cards_container)

        # --- Sección de Plugins (se rellena dinámicamente) ---
        self.plugins_section = QWidget()
        self.plugins_section.hide()  # oculto hasta que se agregue al menos un plugin
        plugins_section_layout = QVBoxLayout(self.plugins_section)
        plugins_section_layout.setContentsMargins(0, 10, 0, 0)
        plugins_section_layout.setSpacing(10)

        # Separador visual
        separator_label = QLabel("Plugins instalados")
        separator_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #95a5a6;
            padding-bottom: 4px;
            border-bottom: 1px solid #dce1e7;
        """)
        plugins_section_layout.addWidget(separator_label)

        self.plugins_cards_container = QWidget()
        self.plugins_cards_layout = FlowLayout(self.plugins_cards_container, spacing=20)
        plugins_section_layout.addWidget(self.plugins_cards_container)

        main_layout.addWidget(self.plugins_section)
        
        # Mensaje de bienvenida inferior
        welcome_label = QLabel("Bienvenido a Pyme Tool. Seleccione una sección para comenzar.")
        welcome_label.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-top: 20px;")
        main_layout.addWidget(welcome_label, alignment=Qt.AlignCenter)

        main_layout.addStretch(1)

        self.scroll_area.setWidget(self.container)
        outer_layout.addWidget(self.scroll_area)
        self.setLayout(outer_layout)

    def add_plugin_card(self, plugin_name: str, icon_path: str, callback):
        """Agrega un card de plugin a la sección de Plugins en el Home."""
        card = CardWidget(plugin_name, icon_path)
        card.clicked.connect(callback)
        self.plugins_cards_layout.addWidget(card)
        self.plugins_section.show()

    def clear_plugin_cards(self):
        """Elimina todos los cards de plugins del Home (para recargarlos)."""
        # Vaciar el FlowLayout quitando todos los widgets
        while self.plugins_cards_layout.count():
            item = self.plugins_cards_layout.takeAt(0)
            w = item.widget() if item else None
            if w:
                w.setParent(None)
                w.deleteLater()
        self.plugins_section.hide()
