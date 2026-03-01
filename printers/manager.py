import os
import importlib
import inspect
from .base import BasePrinter

class PrinterManager:
    """
    Gestiona la carga dinámica de drivers desde la carpeta printers/
    """
    
    @staticmethod
    def get_available_drivers():
        drivers = {}
        printers_dir = os.path.dirname(__file__)
        
        for filename in os.listdir(printers_dir):
            if filename.endswith(".py") and filename not in ["base.py", "manager.py", "__init__.py"]:
                module_name = f"printers.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BasePrinter) and obj is not BasePrinter:
                            drivers[filename[:-3]] = obj
                except Exception as e:
                    print(f"Error cargando driver {filename}: {e}")
        
        return drivers

    @staticmethod
    def get_printer_instance(driver_name, printer_name=None):
        drivers = PrinterManager.get_available_drivers()
        if driver_name in drivers:
            return drivers[driver_name](printer_name)
        return None
