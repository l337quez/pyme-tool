import sqlite3
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QAbstractItemView, QFrame, QDialog, QPushButton, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PySide6.QtGui import QPainter

class TransactionDetailDialog(QDialog):
    def __init__(self, date, buyer, seller, items_data):
        super().__init__()
        self.setWindowTitle("Detalle de Transacción")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Info de la cabecera
        header = QLabel(f"<b>Fecha:</b> {date}<br><b>Cliente:</b> {buyer}<br><b>Vendedor:</b> {seller}")
        header.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Tabla de productos
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Producto", "Precio Unit.", "Monto Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        total_monto = 0
        self.table.setRowCount(len(items_data))
        for i, (name, price) in enumerate(items_data):
            self.table.setItem(i, 0, QTableWidgetItem(str(name)))
            self.table.setItem(i, 1, QTableWidgetItem(f"$ {price:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"$ {price:.2f}"))
            total_monto += price
            
        layout.addWidget(self.table)
        
        # Total
        footer = QLabel(f"TOTAL: $ {total_monto:.2f}")
        footer.setAlignment(Qt.AlignRight)
        footer.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60; margin-top: 10px;")
        layout.addWidget(footer)
        
        # Boton cerrar
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("padding: 8px; background-color: #34495e; color: white; border-radius: 5px;")
        layout.addWidget(btn_close)

class ReportsTab(QWidget):
    def __init__(self):
        super().__init__()

        # Conexión a la base de datos
        self.conexion_db = sqlite3.connect('pyme_tool_data_base.db')
        self.cursor = self.conexion_db.cursor()

        # Layout EXTERNO para el ScrollArea
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent;")
        
        # Contenedor para el contenido real
        self.content_widget = QWidget()
        self.content_widget.setObjectName("ReportsContent")
        self.content_widget.setStyleSheet("#ReportsContent { background-color: transparent; }")
        
        # Layout real contenido en el widget
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Título
        title_label = QLabel("Dashboard de Reportes")
        title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # Panel de Resumen (Stats)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_sales_card = self.create_stat_card("VENTAS TOTALES", "$ 0.00", "#27ae60")
        self.total_items_card = self.create_stat_card("PRODUCTOS VENDIDOS", "0", "#2980b9")
        self.total_transactions_card = self.create_stat_card("TRANSACCIONES", "0", "#8e44ad")

        stats_layout.addWidget(self.total_sales_card)
        stats_layout.addWidget(self.total_items_card)
        stats_layout.addWidget(self.total_transactions_card)
        
        layout.addLayout(stats_layout)

        # Panel de Gráficos
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # 1. Gráfico Top Salidas (Pie)
        self.pie_chart_view = QChartView()
        self.pie_chart_view.setRenderHint(QPainter.Antialiasing)
        self.pie_chart_view.setMinimumHeight(300)
        
        # 2. Gráfico Valorizados (Donut)
        self.donut_chart_view = QChartView()
        self.donut_chart_view.setRenderHint(QPainter.Antialiasing)
        self.donut_chart_view.setMinimumHeight(300)

        charts_layout.addWidget(self.pie_chart_view)
        charts_layout.addWidget(self.donut_chart_view)
        
        layout.addLayout(charts_layout)

        # Espaciador para separar gráficos de la tabla
        layout.addSpacing(10)

        # Sección de Transacciones
        table_container = QWidget()
        table_vbox = QVBoxLayout(table_container)
        table_vbox.setContentsMargins(0, 10, 0, 0)

        table_label = QLabel("Historial de Transacciones (Doble clic para detalles)")
        table_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #34495e; margin-bottom: 10px;")
        table_vbox.addWidget(table_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Fecha", "Cliente", "Vendedor", "Items", "Total ($)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMinimumHeight(400) 
        self.table.setMaximumHeight(800)
        self.table.itemDoubleClicked.connect(self.mostrar_detalle_transaccion)
        table_vbox.addWidget(self.table)
        
        layout.addWidget(table_container)

        # Ensamblaje final de ScrollArea
        self.scroll_area.setWidget(self.content_widget)
        outer_layout.addWidget(self.scroll_area)

        self.cargar_datos()

    def showEvent(self, event):
        super().showEvent(event)
        self.cargar_datos()

    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-left: 6px solid {color};
                border-radius: 10px;
            }}
            QLabel {{ border: none; }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        t_label = QLabel(title)
        t_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;")
        
        v_label = QLabel(value)
        v_label.setStyleSheet(f"font-size: 26px; color: {color}; font-weight: bold;")
        v_label.setObjectName("value_label")
        
        card_layout.addWidget(t_label)
        card_layout.addWidget(v_label)
        return card

    def cargar_datos(self):
        query = """
            SELECT s.date, s.buyer, s.seller, COUNT(s.id), SUM(p.price) 
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY s.date, s.buyer, s.seller
            ORDER BY s.date DESC
        """
        self.cursor.execute(query)
        transactions = self.cursor.fetchall()
        
        self.table.setRowCount(0)
        total_facturado = 0
        total_items_vendidos = 0
        
        for row, data in enumerate(transactions):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(data[0])))
            self.table.setItem(row, 1, QTableWidgetItem(str(data[1])))
            self.table.setItem(row, 2, QTableWidgetItem(str(data[2])))
            self.table.setItem(row, 3, QTableWidgetItem(str(data[3])))
            self.table.setItem(row, 4, QTableWidgetItem(f"$ {data[4]:.2f}"))
            
            total_facturado += data[4]
            total_items_vendidos += data[3]

        self.total_sales_card.findChild(QLabel, "value_label").setText(f"$ {total_facturado:.2f}")
        self.total_items_card.findChild(QLabel, "value_label").setText(str(total_items_vendidos))
        self.total_transactions_card.findChild(QLabel, "value_label").setText(str(len(transactions)))

        self.update_pie_chart()
        self.update_donut_chart(total_facturado, total_items_vendidos)

    def mostrar_detalle_transaccion(self, item):
        row = item.row()
        date = self.table.item(row, 0).text()
        buyer = self.table.item(row, 1).text()
        seller = self.table.item(row, 2).text()
        
        query = """
            SELECT p.name, p.price
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.date = ? AND s.buyer = ? AND s.seller = ?
        """
        self.cursor.execute(query, (date, buyer, seller))
        items_data = self.cursor.fetchall()
        
        dialog = TransactionDetailDialog(date, buyer, seller, items_data)
        dialog.exec()

    def update_pie_chart(self):
        query = """
            SELECT p.name, COUNT(s.id) as total
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.name
            ORDER BY total DESC
            LIMIT 5
        """
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        series = QPieSeries()
        for name, count in data:
            slice = series.append(name, count)
            slice.setLabelVisible(True)
            slice.setLabel(f"{name} ({count})")

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Productos Más Vendidos")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.setTheme(QChart.ChartThemeLight)
        
        self.pie_chart_view.setChart(chart)

    def update_donut_chart(self, total_facturado, total_salidas):
        self.cursor.execute("SELECT SUM(quantity * price) FROM products")
        total_entradas = self.cursor.fetchone()[0] or 0
        
        series = QPieSeries()
        series.setHoleSize(0.35)
        
        series.append("Valor Stock (Entradas)", total_entradas).setBrush(Qt.blue)
        series.append("Total Facturado", total_facturado).setBrush(Qt.yellow)
        series.append("Cantidad Salidas", total_salidas).setBrush(Qt.red)

        for slice in series.slices():
            slice.setLabelVisible(True)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Balance Valorizado")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.setTheme(QChart.ChartThemeLight)
        
        self.donut_chart_view.setChart(chart)
