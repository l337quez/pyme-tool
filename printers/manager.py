import os
import importlib
import inspect
from .base import BasePrinter

class PrinterManager:
    """
    Gestiona la carga de drivers
    """
    
    @staticmethod
    def get_available_drivers():
        drivers = {}
        try:
            from . import goojprt
            driver_modules = {'goojprt': goojprt}
            
            for filename, module in driver_modules.items():
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BasePrinter) and obj is not BasePrinter:
                        drivers[filename] = obj
        except Exception as e:
            print(f"Error cargando drivers: {e}")
        
        return drivers

    @staticmethod
    def get_printer_instance(driver_name, printer_name=None):
        drivers = PrinterManager.get_available_drivers()
        if driver_name in drivers:
            return drivers[driver_name](printer_name)
        return None
