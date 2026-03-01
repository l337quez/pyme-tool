from abc import ABC, abstractmethod

class BasePrinter(ABC):
    """
    Clase base abstracta para drivers de impresoras térmicas. 
    Permite que cada impresora maneje sus propios comandos ESC/POS o específicos.
    """
    
    def __init__(self, printer_name=None):
        self.printer_name = printer_name

    @abstractmethod
    def print_receipt(self, config, receipt_data):
        """
        Imprime un ticket de venta.
        :param config: Diccionario con datos del negocio (nombre, direccion, etc)
        :param receipt_data: Diccionario con datos de la venta (items, total, cliente, etc)
        """
        pass

    @abstractmethod
    def print_label(self, product_data):
        """
        Imprime una etiqueta de producto con código de barras.
        :param product_data: Diccionario con datos del producto (nombre, precio, codigo)
        """
        pass
