<div align="center">

# A2 Downloader

Herramienta `CLI` que permite a usuarios con suscripción descargar cursos para acceso offline, facilitando el estudio desde cualquier lugar y en cualquier momento sin necesidad de conexión a Internet.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GitHub repo size](https://img.shields.io/github/repo-size/alpha-drm/a2-downloader)]()
![GitHub Repo stars](https://img.shields.io/github/stars/alpha-drm/a2-downloader)
![GitHub forks](https://img.shields.io/github/forks/alpha-drm/a2-downloader)
![GitHub watchers](https://img.shields.io/github/watchers/alpha-drm/a2-downloader)
![GitHub top language](https://img.shields.io/github/languages/top/alpha-drm/a2-downloader)
![GitHub Created At](https://img.shields.io/github/created-at/alpha-drm/a2-downloader)
![GitHub last commit](https://img.shields.io/github/last-commit/alpha-drm/a2-downloader)


</div>

> [!NOTE]
> Los gestores de descargas o extensiones utilizan el mismo método para descargar vídeos de una página. Esta herramienta sólo automatiza el proceso de un usuario haciendo esto manualmente en un navegador.

## Características

- No evade sistemas de protección ni accede a contenido sin autorización.
- Requiere autenticación válida del usuario.
- Funciona desde la línea de comandos (CLI).
- Automatiza la navegación web mediante Chrome.
- Descarga videos y otros recursos disponibles.
- Permite reanudar descargas interrumpidas.
- Organiza el contenido de forma estructurada.
- Ideal para uso personal y educativo en modo offline.

## Requisitos

- Tener acceso a los cursos.
- [Google Chrome](https://www.google.com/intl/es_us/chrome/) (actualizado)
- [git](https://git-scm.com/) (para clonar el repositorio)
- [Python >=3.11](https://python.org/) (Añadirlo al PATH durante la instalación)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp/)
- [ffmpeg](https://ffmpeg.org/)
- [aria2/aria2c](https://github.com/aria2/aria2/)

## Instalación

- Crear una carpeta llamada `tools` o el nombre que quieran en en el disco `C:\`, dentro copiar los ejecutables (yt-dlp, ffmpeg, aria2c) y por último agregar la ruta de la carpeta al `PATH` del sistema.

- Opcional: copiar los ejecutables directamente en el directorio raíz del proyecto.

Estructura final: `C:\tools`

```bash
C:\tools
   |── yt-dlp.exe
   |── ffmpeg.exe
   └── aria2c.exe
```

### Windows

Clonar el proyecto usando GIT, o simplemente descargar el archivo `ZIP` del repositorio

```bash
git clone https://github.com/alpha-drm/a2-downloader

```

Ir al directorio del proyecto

```bash
cd a2-downloader
```

#### Entorno virtual
  Es recomendable crear un entorno virtual para instalar los `requirements.txt` del proyecto
```bash
python -m venv env
```

  Activar el entorno virtual
```bash
env\Scripts\activate
```

#### Instalar las dependencias

```bash
pip install -r requirements.txt
```

## Cookies

> [!IMPORTANT]
> Estar logueado en la plataforma, usar `firefox` preferiblemente.

El script utiliza cookies para autenticación y lo extrae automáticamente. Opcional, puedes especificar de que navegador extraer las cookies con el argumento `--browser`. Las opciones son:

- `firefox` por defecto, recomendado.
- `chrome`
- `edge`
- `brave`

## Instrucciones de uso

```bash
python main.py <url> [OPCIONES]
```
Opciones:
- `--browser` Navegador de donde extraer las cookies {firefox, chrome, edge, brave}

Ejemplos:

Descargar usando las cookies del navegador por defecto `firefox`:
```bash
python main.py https://cursos.a2capacitacion.com/courses/105117/lectures/50050151
```

Descargar usando las cookies de otro navegador:
```bash
python main.py https://cursos.a2capacitacion.com/courses/105117/lectures/50050151 --browser edge
```

> [!WARNING]
> Al finalizar la descarga de un curso es posible que los procesos de chrome no se hayan cerrado correctamente, es un error con el 
undetected-chromedriver que no he podido resolver,  revisar el administrador de tareas y finalizarlos para no consumir recursos.

## Feedback

Para comentarios o reportes de errores utilizar [GitHub Issues](https://github.com/alpha-drm/a2-downloader/issues) 

## License

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](https://github.com/alpha-drm/a2-downloader/blob/main/LICENSE) para más detalles.

## Aviso Legal

Este proyecto tiene fines exclusivamente educativos y personales. El autor no se responsabiliza por el uso indebido de esta herramienta. El acceso y la descarga de contenidos están permitidos únicamente a usuarios con credenciales válidas y acceso legítimo a los cursos en la plataforma.

Es responsabilidad exclusiva del usuario:
- Cumplir con los Términos de Servicio y Condiciones de Uso de la plataforma.
- Respetar las leyes de derechos de autor, de propiedad intelectual y cualquier otra normativa local aplicable.
- Abstenerse de redistribuir, revender, publicar o compartir los contenidos descargados mediante este script.
- El propósito de esta herramienta es facilitar el acceso offline para usuarios autorizados, y no debe utilizarse con fines comerciales.