"""
A2-Downloader

Licencia: MIT
Copyright (c) 2025 alpha

Este script se proporciona exclusivamente con fines educativos.
El autor no se hace responsable del uso indebido del mismo.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
import json
import os
import browser_cookie3
import time
import logging
import coloredlogs
from colorama import Fore, Back, init
from bs4 import BeautifulSoup
from pyfiglet import Figlet
import subprocess
import argparse
import re
from typing import Dict, Any, Optional

# --- CONFIGURACIÓN DE LOGGING ---
LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(asctime)s] [%(name)s] [%(funcName)s:%(lineno)d] [%(levelname)s]: %(message)s'
LOG_DATE_FORMAT = '%d-%m-%Y %H:%M:%S'
LOG_STYLES = {
    'info': {'color': 'white'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red'},
    'critical': {'bold': True, 'color': 'red'}
}
LOG_DIR = "logs"

# Crear directorio de logs si no existe
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = f"{time.strftime('%d-%m-%Y_%H-%M-%S')}.log"
log_filepath = os.path.join(LOG_DIR, log_filename)

logger = logging.getLogger('A2-Downloader')
coloredlogs.install(level=LOG_LEVEL, logger=logger, fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level_styles=LOG_STYLES)

# Handler para el archivo de log
file_handler = logging.FileHandler(log_filepath, mode='w', encoding='utf-8')
file_handler.setLevel(LOG_LEVEL)
log_format_file = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(funcName)s]: %(message)s', datefmt=LOG_DATE_FORMAT)
file_handler.setFormatter(log_format_file)
logger.addHandler(file_handler)

# --- FUNCIONES AUXILIARES ---

def banner():
    """Muestra el banner del script."""
    init(autoreset=True)
    font = Figlet(font='slant')
    script_title = 'A2-Downloader'
    print(Fore.GREEN + font.renderText(script_title))
    print(Back.GREEN + "Created by alphaDRM")
    print()

def sanitize_filename(name: str) -> str:
    """Limpia una cadena para que sea un nombre de archivo/carpeta válido."""
    # Elimina caracteres no permitidos en nombres de archivo/carpeta
    cleaned_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Elimina espacios al inicio y final
    cleaned_name = cleaned_name.strip()
    return cleaned_name

def clean_lesson_name(name: str) -> str:
    """Elimina la duración del video (ej. (12:34)) del nombre de la lección."""
    return re.sub(r'\s*\(\d{1,2}:\d{2}\)\s*', '', name).strip()

# --- FUNCIONES DE SCRAPING Y EXTRACCIÓN ---

def scrape_course_structure(course_url: str, browser: str, base_url: str) -> Optional[Dict[str, Any]]:
    """Extrae la estructura del curso (secciones y lecciones) usando requests."""
    logger.info("Obteniendo la estructura del curso...")
    try:
        if browser == "firefox":
            cj = browser_cookie3.firefox(domain_name="a2capacitacion")
        elif browser == "chrome":
            cj = browser_cookie3.chrome(domain_name="a2capacitacion")
        elif browser == "edge":
            cj = browser_cookie3.edge(domain_name="a2capacitacion")
        elif browser == "brave":
            cj = browser_cookie3.brave(domain_name="a2capacitacion")

        if not cj:
            logger.error("No se pudo obtener las cookies del navegador, debes iniciar sesión en el navegador seleccionado.")
            return None

        session_cookies = {cookie.name: cookie.value for cookie in cj}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        with requests.Session() as session:
            session.headers.update(headers)
            session.cookies.update(session_cookies)
            response = session.get(course_url)
            response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        course_title_tag = soup.find('div', class_='course-sidebar-head')
        if not course_title_tag or not course_title_tag.h2:
             logger.error("No se pudo encontrar el título del curso.")
             return None
        course_title = course_title_tag.h2.get_text(strip=True)

        course_data = {
            "course_title": sanitize_filename(course_title),
            "secciones": []
        }

        for section in soup.find_all('div', class_='course-section'):
            section_title_tag = section.find('div', class_='section-title')
            if not section_title_tag: continue  # noqa: E701

            section_title = clean_lesson_name(section_title_tag.get_text(strip=True))

            lessons = []
            for item in section.select('li.section-item a.item'):
                lesson_name = item.find('span', class_='lecture-name').get_text(strip=True)
                lesson_url = f"{base_url}{item.get('href')}"
                lessons.append({
                    "name": clean_lesson_name(lesson_name),
                    "url": lesson_url
                })

            course_data["secciones"].append({
                "titulo_seccion": sanitize_filename(section_title),
                "lecciones": lessons
            })

        logger.info(f"Estructura del curso '{course_title}' extraída con éxito.")
        return course_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error al intentar obtener la estructura del curso: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado durante el scraping: {e}")
        return None

# --- FUNCIONES DE DESCARGA ---

def download_cover_image(driver: uc.Chrome, save_dir: str):
    """Descarga la imagen de portada del curso."""
    try:
        cover_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "meta[property='og:image']"))
        )
        cover_url = cover_element.get_attribute('content')

        ext = cover_url.split('.')[-1].split('?')[0] # Limpia parámetros de URL
        image_path = os.path.join(save_dir, f'cover.{ext}')

        response = requests.get(cover_url, stream=True)
        response.raise_for_status()
        with open(image_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info('Imagen de portada descargada exitosamente.')
    except (TimeoutException, requests.RequestException) as e:
        logger.warning(f"No se pudo descargar la imagen de portada: {e}")

def download_lesson_resources(driver: uc.Chrome, save_path: str):
    """Descarga archivos adjuntos y guarda enlaces de una lección."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')  
    # Descargar archivos adjuntos
    for link in soup.find_all('a', class_='download'):
        url = link['href']
        filename = sanitize_filename(link.get('data-x-origin-download-name', link.text.strip()))
        file_path = os.path.join(save_path, filename)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Recurso '{filename}' descargado.")
        except requests.RequestException as e:
            logger.error(f"Error al descargar recurso '{filename}': {e}")

    # Guardar enlaces adicionales
    count = 0
    lecture_container = soup.find('div', class_='lecture-text-container')
    if lecture_container:
        links = [a['href'] for a in lecture_container.find_all('a', href=True)]
        if len(links) > 0:
            count +=1
            links_path = os.path.join(save_path, f"enlaces_adicionales_{count}.txt")
            with open(links_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(links))
            logger.info("Enlaces adicionales guardados en 'enlaces_adicionales.txt'.")

def download_lesson_video(driver: uc.Chrome, save_path: str, lesson_filename: str):
    """Encuentra y descarga el video de la lección usando yt-dlp."""
    try:
        iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[data-testid='embed-player']"))
        )
        driver.switch_to.frame(iframe)

        script_tag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))
        )
        
        json_data = json.loads(script_tag.get_attribute('innerHTML'))
        media_assets = json_data.get('props', {}).get('pageProps', {}).get('applicationData', {}).get('mediaAssets', [])

        if not media_assets:
            logger.warning("No se encontraron 'mediaAssets' en los datos del video.")
            return

        # Prioriza 'auto' para obtener el manifiesto HLS/DASH
        video_url = next((asset['url'] for asset in media_assets if asset.get('qualityLabel') == "auto"), None)
        if not video_url: # Si no hay 'auto', toma la primera URL que encuentre
             video_url = media_assets[0].get('url') if media_assets else None
        
        if video_url:
            logger.info(f"Descargando video: {lesson_filename}")
            command = [
                "yt-dlp",
                "--add-headers", "Referer: https://player.hotmart.com/",
                "--downloader", "aria2c", # Usa aria2c para descargas más rápidas
                "-P", save_path,
                "-o", f"{lesson_filename}.%(ext)s",
                video_url
            ]
            process = subprocess.Popen(command)
            process.wait()
            if process.returncode != 0:
                logger.error(f"yt-dlp falló para '{lesson_filename}'.")
            else:
                 logger.info(f"Video '{lesson_filename}' descargado con éxito.")
        else:
            logger.warning("No se encontró una URL de video válida en 'mediaAssets'.")

    except TimeoutException:
        logger.info("No se encontró video en esta lección.")
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error al procesar los datos del video: {e}")
    finally:
        driver.switch_to.default_content()

# --- FUNCIÓN PRINCIPAL DE PROCESAMIENTO ---

def process_course(course_url: str, course_data: Dict[str, Any]):
    """Proceso de descarga del curso."""
    driver = None
    start_time = time.time()
    
    try:
        logger.info("Iniciando el navegador...")
        driver = uc.Chrome()
        driver.maximize_window()
        driver.get(course_url)

        # Cargar cookies en Selenium
        cj = browser_cookie3.firefox(domain_name="a2capacitacion")
        for cookie in cj:
            driver.add_cookie({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path
            })
        driver.refresh()
        logger.info("Cookies cargadas en el navegador.")

        base_dir = course_data['course_title']
        os.makedirs(base_dir, exist_ok=True)
        
        download_cover_image(driver, base_dir)

        total_lessons = sum(len(sec["lecciones"]) for sec in course_data["secciones"])
        lesson_count = 0

        for section in course_data["secciones"]:
            section_title = section["titulo_seccion"]
            section_path = os.path.join(base_dir, section_title)
            os.makedirs(section_path, exist_ok=True)
            logger.info(f"--- Procesando sección: {section_title} ---")
            
            for i, lesson in enumerate(section["lecciones"]):
                lesson_count += 1
                lesson_title = f"{i+1:02d} - {lesson['name']}"
                lesson_filename = sanitize_filename(lesson_title)
                lesson_url = lesson["url"]
                
                logger.info(f"Procesando lección {lesson_count}/{total_lessons}: {lesson['name']}")
                driver.get(lesson_url)
                
                try:
                    # Espera a que el contenido principal de la lección cargue
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "lecture_heading"))
                    )
                except TimeoutException:
                    logger.error(f"La página de la lección '{lesson_title}' no cargó correctamente. Saltando...")
                    continue
                
                download_lesson_resources(driver, section_path)
                download_lesson_video(driver, section_path, lesson_filename)

    except WebDriverException as e:
        logger.critical(f"Error con el WebDriver de Selenium: {e}")
    except Exception as e:
        logger.critical(f"Ha ocurrido un error inesperado en el proceso principal: {e}")
    finally:
        if driver:
            driver.quit()
            logger.info("El navegador se ha cerrado.")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Descarga Finalizada. Duración total: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")
        logger.info("*** Created by alphaDRM ***")

# --- INICIO DEL SCRIPT ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A2 Downloader",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "url",
        help="La URL completa del curso a descargar."
    )
    # Argumento opcional para el navegador
    parser.add_argument(
        "--browser",
        help="Navegador para extraer las cookies. Por defecto: firefox.",
        choices=["firefox", "chrome", "edge", "brave"],
        default="firefox",
    )

    args = parser.parse_args()

    if args.browser:
        browser = args.browser

    BASE_URL = "https://cursos.a2capacitacion.com"

    banner()

    # 1. Extraer la estructura del curso
    course_structure = scrape_course_structure(args.url, browser, BASE_URL)

    if course_structure:
        # 2. Guardar la estructura en un archivo JSON (para depuración)
        json_output_file = f"{course_structure['course_title']}.json"
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(course_structure, f, ensure_ascii=False, indent=4)
        logger.info(f"Estructura del curso guardada en: {json_output_file}")

        # 3. Iniciar el proceso de descarga
        process_course(args.url, course_structure)
