import urllib.request
import zipfile
import os
import shutil
import time
import sys
import subprocess

def update_app():
    print("========================================")
    print("      Actualizador de PYME Tool         ")
    print("========================================")
    print("Esperando a que la aplicacion se cierre (3 segundos)...")
    time.sleep(3)
    
    url = "https://github.com/l337quez/pyme-tool/archive/refs/heads/main.zip"
    zip_path = "update.zip"
    extract_folder = "pyme-tool-main"
    
    print("Descargando actualizacion desde el repositorio...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        print(f"Error descargando la actualizacion: {e}")
        input("Presiona Enter para salir...")
        return
        
    print("Extrayendo archivos...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall()
    except Exception as e:
        print(f"Error al extraer el archivo zip: {e}")
        input("Presiona Enter para salir...")
        return

    print("Instalando los nuevos archivos...")
    ignore_files = ['pyme_tool_data_base.db', 'inventory.db', 'tu_basededatos.sqlite', 'settings.json']
    
    installed_files = 0
    for root, dirs, files in os.walk(extract_folder):
        rel_path = os.path.relpath(root, extract_folder)
        if rel_path == ".":
            dest_dir = "."
        else:
            dest_dir = rel_path
            os.makedirs(dest_dir, exist_ok=True)
            
        for file in files:
            if file in ignore_files and dest_dir == ".":
                print(f"Omitiendo archivo de base de datos/config: {file}")
                continue
            
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)
            try:
                if os.path.exists(dest_file):
                    os.remove(dest_file)
                shutil.copy2(src_file, dest_file)
                installed_files += 1
            except Exception as e:
                print(f"Advertencia: No se pudo actualizar el archivo {file}: {e}")

    print(f"Se actualizaron {installed_files} archivos.")

    print("Limpiando archivos temporales...")
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)
    except Exception as e:
        print(f"Advertencia al limpiar la cache de actualizacion: {e}")

    print("========================================")
    print("¡La actualizacion se ha completado con exito!")
    print("Reiniciando PYME Tool...")
    time.sleep(2)
    
    try:
        subprocess.Popen([sys.executable, 'main.py'])
    except Exception as e:
        print(f"Error al reiniciar la aplicacion: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    update_app()
