from .base import BasePrinter
import os

class GoojprtPrinter(BasePrinter):
    """
    Driver para impresoras GOOJPRT / ESC-POS Genéricas (58mm/80mm).
    """

    def print_receipt(self, config, receipt_data):
        line = "-" * 32 + "\n"
        ticket = []
        
        # Cabecera
        ticket.append(f"{config.get('business_name', 'MI NEGOCIO').center(32)}\n")
        ticket.append(f"ID: {config.get('business_id', '-')}\n")
        ticket.append(f"TEL: {config.get('phone', '-')}\n")
        ticket.append(f"DIR: {config.get('address', '-')[:32]}\n")
        ticket.append(line)
        
        # Info Venta
        ticket.append(f"FECHA: {receipt_data.get('date')}\n")
        ticket.append(f"CLIENTE: {receipt_data.get('buyer', 'General')}\n")
        ticket.append(f"VENDEDOR: {receipt_data.get('seller', '-')}\n")
        ticket.append(line)
        
        # Items
        ticket.append(f"{'PRODUCTO'.ljust(15)} {'CANT'.center(4)} {'TOTAL'.rjust(10)}\n")
        for item in receipt_data.get('items', []):
            name = item['name'][:15]
            cant = str(item['quantity'])
            total = f"{item['price']:.2f}"
            ticket.append(f"{name.ljust(15)} {cant.center(4)} {total.rjust(10)}\n")
        
        ticket.append(line)
        
        # Totales
        moneda = receipt_data.get('currency', 'USD')
        total_val = receipt_data.get('total', 0)
        ticket.append(f"TOTAL: {moneda} {total_val:.2f}\n".rjust(32))
        ticket.append("\n")
        ticket.append("GRACIAS POR SU COMPRA\n".center(32))
        ticket.append("\n" * 4) # Espacio para corte

        ticket_text = "".join(ticket)
        self._send_to_printer(ticket_text)

    def print_label(self, product_data):
        # Implementación básica de etiqueta
        label = []
        label.append("-" * 32 + "\n")
        label.append(f"{product_data.get('name', 'PRODUCTO')[:32].center(32)}\n")
        label.append(f"PRECIO: ${product_data.get('price', 0):.2f}".center(32) + "\n")
        label.append("\n")
        # Simulación de código de barras (solo texto por ahora)
        label.append(f"|| ||| || ||| ||".center(32) + "\n")
        label.append(f"{product_data.get('id', '0000')}".center(32) + "\n")
        label.append("-" * 32 + "\n")
        label.append("\n" * 2)
        
        label_text = "".join(label)
        self._send_to_printer(label_text)

    def _send_to_printer(self, text):
        print(f"--- IMPRIMIENDO EN {self.printer_name or 'GOOJPRT'} ---")
        print(text)
        print("--- FIN DE IMPRESIÓN ---")
        
        # En Windows: Podríamos usar win32print o simplemente un archivo .txt
        with open("last_print.txt", "w", encoding="utf-8") as f:
            f.write(text)
