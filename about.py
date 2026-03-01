from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class AboutTab(QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal centrado
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        # Contenedor para el logo y título
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(120, 120)
        self.logo_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap('assets/pyme-tools-logo.png')
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo_label.setText("LOGO")
            self.logo_label.setStyleSheet("border: 1px solid #ccc; border-radius: 60px; background-color: #eee;")
        
        header_layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)

        app_name = QLabel("Pyme Tool")
        app_name.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(app_name, alignment=Qt.AlignCenter)

        main_layout.addWidget(header_frame)

        # Información del proyecto (Créditos)
        info_frame = QFrame()
        info_frame.setObjectName("InfoFrame")
        info_frame.setStyleSheet("""
            #InfoFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(20, 20, 20, 20)

        info_data = [
            "Version: v0.1.9 Beta",
            "License: GPL V3",
            "Packaged: Ronal Forero",
            "Translated: Ronal Forero",
            "Tested: Ronal Forero",
            "Designer: Ronal Forero",
            "Development by: Ronal Forero"
        ]

        for text in info_data:
            row_label = QLabel(text)
            row_label.setStyleSheet("""
                QLabel {
                    color: #34495e; 
                    font-size: 14px;
                    background-color: #f9f9f9;
                    border: 1px solid #eee;
                    border-radius: 18px;
                    padding: 8px 20px;
                }
            """)
            row_label.setAlignment(Qt.AlignCenter)
            info_layout.addWidget(row_label)

        main_layout.addWidget(info_frame)

        # Footer
        footer_label = QLabel("© 2023 Ronal Forero - Todos los derechos reservados")
        footer_label.setStyleSheet("color: #95a5a6; font-size: 11px; margin-top: 20px;")
        main_layout.addWidget(footer_label, alignment=Qt.AlignCenter)

        main_layout.addStretch()
