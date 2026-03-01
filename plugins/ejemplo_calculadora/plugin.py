"""
Plugin de ejemplo: Calculadora Simple
======================================
Este plugin sirve como referencia para que otras personas puedan
crear sus propios plugins. Sigue la estructura de BasePlugin.

Para crear tu propio plugin, copia esta carpeta y modifica:
  - name, icon, show_in_home, tab_label
  - El método create_widget() con tu propia UI
"""

import os
from plugin_base import BasePlugin
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QGridLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class Plugin(BasePlugin):
    # --- Metadatos del plugin ---
    name = "Calculadora"
    icon = "icon.png"       # relativo a esta carpeta (plugins/ejemplo_calculadora/)
    show_in_home = True
    tab_label = "Calculadora"

    def create_widget(self) -> QWidget:
        """Retorna la UI de la calculadora."""
        widget = QWidget()
        widget.setObjectName("CalculadoraPlugin")
        widget.setStyleSheet("""
            #CalculadoraPlugin {
                background-color: #f5f6fa;
            }
        """)

        outer = QVBoxLayout(widget)
        outer.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        outer.setContentsMargins(40, 40, 40, 40)

        # Título
        title = QLabel("🧮 Calculadora")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        outer.addWidget(title)

        # Contenedor de la calculadora
        calc_container = QWidget()
        calc_container.setFixedWidth(320)
        calc_container.setObjectName("CalcBox")
        calc_container.setStyleSheet("""
            #CalcBox {
                background: white;
                border-radius: 16px;
                border: 1px solid #e0e0e0;
            }
        """)

        calc_layout = QVBoxLayout(calc_container)
        calc_layout.setContentsMargins(20, 20, 20, 20)
        calc_layout.setSpacing(12)

        # Display
        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet("""
            QLineEdit {
                background: #f0f4f8;
                border: 1px solid #d0d8e0;
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        calc_layout.addWidget(self.display)

        # Botones
        btn_style_num = """
            QPushButton {
                background: #ecf0f1; border-radius: 10px;
                font-size: 18px; font-weight: bold; color: #2c3e50;
                border: 1px solid #d5dbdb; padding: 14px;
            }
            QPushButton:hover { background: #dde4ea; }
            QPushButton:pressed { background: #c8d6df; }
        """
        btn_style_op = """
            QPushButton {
                background: #3498db; border-radius: 10px;
                font-size: 18px; font-weight: bold; color: white;
                border: none; padding: 14px;
            }
            QPushButton:hover { background: #2980b9; }
            QPushButton:pressed { background: #1f6fa3; }
        """
        btn_style_eq = """
            QPushButton {
                background: #2ecc71; border-radius: 10px;
                font-size: 18px; font-weight: bold; color: white;
                border: none; padding: 14px;
            }
            QPushButton:hover { background: #27ae60; }
            QPushButton:pressed { background: #1e8449; }
        """
        btn_style_clear = """
            QPushButton {
                background: #e74c3c; border-radius: 10px;
                font-size: 18px; font-weight: bold; color: white;
                border: none; padding: 14px;
            }
            QPushButton:hover { background: #c0392b; }
            QPushButton:pressed { background: #a93226; }
        """

        grid = QGridLayout()
        grid.setSpacing(8)

        buttons = [
            ("C",   0, 0, btn_style_clear), ("±",  0, 1, btn_style_op),
            ("%",   0, 2, btn_style_op),    ("÷",  0, 3, btn_style_op),

            ("7",   1, 0, btn_style_num),   ("8",  1, 1, btn_style_num),
            ("9",   1, 2, btn_style_num),   ("×",  1, 3, btn_style_op),

            ("4",   2, 0, btn_style_num),   ("5",  2, 1, btn_style_num),
            ("6",   2, 2, btn_style_num),   ("−",  2, 3, btn_style_op),

            ("1",   3, 0, btn_style_num),   ("2",  3, 1, btn_style_num),
            ("3",   3, 2, btn_style_num),   ("+",  3, 3, btn_style_op),

            ("0",   4, 0, btn_style_num),   (".",  4, 1, btn_style_num),
            ("⌫",   4, 2, btn_style_op),    ("=",  4, 3, btn_style_eq),
        ]

        self._expression = ""

        for label, row, col, style in buttons:
            btn = QPushButton(label)
            btn.setStyleSheet(style)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(54)
            btn.clicked.connect(lambda checked=False, l=label: self._on_button(l))
            grid.addWidget(btn, row, col)

        calc_layout.addLayout(grid)
        outer.addWidget(calc_container, alignment=Qt.AlignHCenter)

        return widget

    def _on_button(self, label: str):
        """Lógica de la calculadora."""
        display = self.display

        if label == "C":
            self._expression = ""
            display.setText("0")

        elif label == "⌫":
            self._expression = self._expression[:-1]
            display.setText(self._expression if self._expression else "0")

        elif label == "=":
            try:
                expr = (self._expression
                        .replace("×", "*")
                        .replace("÷", "/")
                        .replace("−", "-"))
                result = eval(expr)
                # Mostrar entero si no tiene decimales
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                display.setText(str(result))
                self._expression = str(result)
            except Exception:
                display.setText("Error")
                self._expression = ""

        elif label == "±":
            try:
                val = float(self._expression or "0") * -1
                self._expression = str(int(val) if float(val).is_integer() else val)
                display.setText(self._expression)
            except Exception:
                pass

        elif label == "%":
            try:
                val = float(self._expression or "0") / 100
                self._expression = str(int(val) if float(val).is_integer() else val)
                display.setText(self._expression)
            except Exception:
                pass

        else:
            if self._expression == "" and label in "×÷−+":
                return
            self._expression += label
            display.setText(self._expression)
