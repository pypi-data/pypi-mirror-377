import sys
import time

import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
import pyautogui
from typing import Optional, Tuple


def resource_path(relative_path):
    """ Devuelve la ruta absoluta para archivos empaquetados con PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda el path en _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Cuando se ejecuta desde Python normal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Detecta la raíz del proyecto (donde está tu script principal)
BASE_DIR = Path.cwd()  # Current Working Directory
dotenv_path = resource_path(".env")

# Carga variables del .env
load_dotenv(dotenv_path)


def enviar_traza_a_graylog(host, message, level="INFO"):
    # Mapeo de niveles de log a valores numéricos

    level_map = {
        "EMERGENCY": 0,
        "ALERT": 1,
        "CRITICAL": 2,
        "ERROR": 3,
        "WARNING": 4,
        "NOTICE": 5,
        "INFO": 6,
        "DEBUG": 7
    }
    level_numeric = level_map.get(level.upper(), 6)  # Default to INFO (6) if the level is not found

    # Datos GELF en formato JSON
    gelf_message = {
        "version": "1.1",
        "host": host,
        "short_message": message,
        "level": level_numeric
    }

    # Convertir el mensaje GELF a JSON
    json_message = json.dumps(gelf_message)

    try:
        requests.post(os.getenv("GRAYLOG_URL", "https://graylog.premm.es"), data=json_message,
                      headers={'Content-Type': 'application/json'})
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al servidor Graylog: {e}")


def get_chrome_options(disable_images=False, disable_interfaz=True):
    chrome_options = Options()

    # Optimizar el rendimiento
    if disable_interfaz:
        chrome_options.add_argument("--headless")  # Solo si no necesitas una interfaz gráfica
    chrome_options.add_argument("--disable-extensions")
    if disable_images:
        chrome_options.add_argument("--disable-images")

    chrome_options.add_argument("--disk-cache-size=0")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Deshabilitar mensaje
    chrome_options.add_experimental_option("excludeSwitches",
                                           ["enable-automation"])  # Ocultar control de automatización
    chrome_options.add_experimental_option("useAutomationExtension", False)  # Deshabilitar extensión de automatización
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--disable-software-rasterizer")

    return chrome_options


def enviar_mensaje_a_matt_mattermost(mensaje: str, canal: str):
    """
    Envía un mensaje a Matt en Mattermost usando un Incoming Webhook.

    Debes definir en tu .env o variables de entorno:
    - MATTERMOST_URL: URL del webhook de tu canal
    """
    webhook_url = os.getenv("MATTERMOST_URL", "https://chat.premm.es")

    payload = {
        "text": mensaje,
        "channel": canal
    }

    try:
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 200:
            return True
        else:
            print(f"Error al enviar mensaje: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"Error {e}")
        return False


def esperar_elemento_img(imagen: str, timeout: float = 10, intervalo: float = 0.5, confidence: float = 0.8) -> Optional[
    Tuple[int, int]]:
    """
        Espera hasta que la imagen aparezca en pantalla.
        Devuelve la posición (x, y) o None si no aparece en el tiempo límite.
        """
    start = time.time()
    while True:
        try:
            pos = pyautogui.locateCenterOnScreen(imagen, confidence=confidence)

            if pos:
                print(f"✅ Elemento '{imagen}' encontrado en {pos}")
                time.sleep(1)
                return pos

        except Exception as e:
            # Mostrar el error pero seguir intentando
            print(f"⚠️ Error inesperado buscando '{imagen}': {type(e).__name__} - {e}")

        # Verificar timeout
        if time.time() - start > timeout:
            print(f"⌛ Elemento '{imagen}' no encontrado en {timeout}s")
            return None

        time.sleep(intervalo)
