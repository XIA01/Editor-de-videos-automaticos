# Mi Proyecto de Video

Este proyecto es un generador de video automatizado que utiliza diversas librerías de Python para procesar imágenes y audios, aplicando efectos y combinándolos en un video final. El proyecto está modularizado en diferentes archivos y carpetas para facilitar su mantenimiento y extensión.

## Estructura del Proyecto

mi_proyecto_video/
├── README.md
├── requirements.txt
├── main.py
├── utils/
│   ├── __init__.py
│   ├── audio_utils.py
│   ├── image_utils.py
│   └── video_utils.py
├── tests/
│   └── test_main.py
└── data/
    ├── ejecucion/
    │   ├── 1/
    │   │   ├── 1.wav
    │   │   ├── music_1.mp3
    │   │   └── imagenes/
    │   │       ├── 00000-...png
    │   │       └── ...
    │   └── 2/
    └── ...


## Requisitos

- Python 3.8+
- MoviePy
- PyDub
- Pillow
- NumPy
- Gradio

Para instalar las dependencias, ejecuta:

pip install -r requirements.txt

# Uso
Para ejecutar el generador de video a través de la interfaz web, ejecuta:

python main.py
La interfaz permite:

Seleccionar una carpeta de ejecución (por ejemplo, "1", "2" o "Todos").
Elegir la resolución de salida con opciones predefinidas: "1920x1080" (por defecto), "786x480", "Vertical" o "Personalizado" (donde podrás especificar ancho y alto).
Visualizar el resultado y los logs del proceso.

### Explicación General

- **Modularización:**  
  El proyecto está dividido en módulos:
  - `audio_utils.py`: funciones para cargar y procesar audios.
  - `image_utils.py`: funciones para procesar imágenes (redimensionar y centrar usando Pillow).
  - `video_utils.py`: funciones para combinar imágenes y audios en un video final, además de una función para obtener la resolución deseada.
  
- **Interfaz Gradio:**  
  La interfaz permite seleccionar la carpeta de ejecución, la resolución de salida y (si se elige "Personalizado") ingresar el ancho y alto deseado.
  
- **Flujo de Generación:**  
  El programa procesa cada imagen según la resolución seleccionada, carga y procesa los audios, concatena los clips y genera el video final, mostrando los logs del proceso.

Esta estructura te permitirá ir agregando nuevas funciones o efectos en módulos adicionales dentro de la carpeta `utils` o en nuevos directorios como `extensions`.
