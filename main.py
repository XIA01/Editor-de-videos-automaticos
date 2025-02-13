import os
import logging
import tempfile
import numpy as np
from PIL import Image
from pydub import AudioSegment

# Configurar logging para mostrar mensajes en la terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Importar clases y funciones de MoviePy
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from moviepy.audio.AudioClip import CompositeAudioClip

def procesar_imagen(ruta_imagen, tamano_final=(1920, 1080)):
    """
    Abre la imagen usando Pillow, la redimensiona para que su altura sea 1080 (manteniendo la relación de aspecto)
    y la centra sobre un fondo negro de tamaño 1920x1080.
    Devuelve un arreglo NumPy que se puede usar para crear un ImageClip.
    """
    try:
        im = Image.open(ruta_imagen).convert("RGB")
    except Exception as e:
        logging.exception(f"No se pudo abrir la imagen: {ruta_imagen}")
        return None

    w, h = im.size
    nuevo_alto = 1080
    escala = nuevo_alto / h
    nuevo_ancho = int(w * escala)
    # Redimensionar usando LANCZOS (nuevo en Pillow 10+)
    im_resized = im.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    # Crear un fondo negro del tamaño final (1920x1080)
    fondo = Image.new("RGB", tamano_final, (0, 0, 0))
    x_offset = (tamano_final[0] - nuevo_ancho) // 2
    y_offset = (tamano_final[1] - nuevo_alto) // 2
    fondo.paste(im_resized, (x_offset, y_offset))
    
    return np.array(fondo)

def crear_video_en_carpeta(carpeta):
    logging.info(f"Iniciando procesamiento de la carpeta: {carpeta}")

    ruta_imagenes = os.path.join(carpeta, "imagenes")
    if not os.path.exists(ruta_imagenes):
        logging.error(f"La carpeta de imágenes no existe: {ruta_imagenes}")
        return

    try:
        lista_imagenes = sorted(
            archivo for archivo in os.listdir(ruta_imagenes)
            if archivo.lower().endswith((".png", ".jpg", ".jpeg"))
        )
    except Exception as e:
        logging.exception("Error al listar imágenes en la carpeta de imágenes")
        return

    logging.info(f"Se encontraron {len(lista_imagenes)} imágenes en {ruta_imagenes}")

    nombre_carpeta = os.path.basename(carpeta)
    ruta_audio_principal = os.path.join(carpeta, f"{nombre_carpeta}.wav")
    ruta_audio_bg = os.path.join(carpeta, f"music_{nombre_carpeta}.mp3")

    if not os.path.exists(ruta_audio_principal):
        logging.error(f"Audio principal no encontrado: {ruta_audio_principal}")
        return
    if not os.path.exists(ruta_audio_bg):
        logging.error(f"Audio de fondo no encontrado: {ruta_audio_bg}")
        return

    logging.info("Cargando audio principal con MoviePy...")
    try:
        audio_principal = AudioFileClip(ruta_audio_principal)
    except Exception as e:
        logging.exception("Error al cargar el audio principal")
        return

    logging.info("Procesando el audio de fondo con PyDub para ajustar el volumen al 20%...")
    try:
        audio_bg_pydub = AudioSegment.from_file(ruta_audio_bg)
        audio_bg_pydub = audio_bg_pydub - 14
        tmp_bg_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_bg_file.close()
        audio_bg_pydub.export(tmp_bg_file.name, format="mp3")
        audio_bg = AudioFileClip(tmp_bg_file.name)
    except Exception as e:
        logging.exception("Error al procesar el audio de fondo con PyDub")
        return

    duracion_total = audio_principal.duration
    logging.info(f"Duración total del audio principal: {duracion_total} segundos")

    num_imagenes = len(lista_imagenes)
    if num_imagenes == 0:
        logging.error("No se encontraron imágenes para procesar")
        return

    duracion_imagen = duracion_total / num_imagenes
    logging.info(f"Cada imagen tendrá una duración de: {duracion_imagen} segundos")

    clips = []
    for idx, imagen in enumerate(lista_imagenes, start=1):
        ruta_imagen = os.path.join(ruta_imagenes, imagen)
        logging.info(f"Procesando imagen {idx}/{num_imagenes}: {ruta_imagen}")
        try:
            img_array = procesar_imagen(ruta_imagen, tamano_final=(1920, 1080))
            if img_array is None:
                continue
            clip_imagen = ImageClip(img_array, duration=duracion_imagen)
            clips.append(clip_imagen)
        except Exception as e:
            logging.exception(f"Error al procesar la imagen: {ruta_imagen}")
            continue

    if not clips:
        logging.error("No se pudieron procesar clips de imagen correctamente.")
        return

    logging.info("Concatenando clips de imagen...")
    try:
        video = concatenate_videoclips(clips, method="compose")
    except Exception as e:
        logging.exception("Error al concatenar clips de imagen")
        return

    logging.info("Ajustando audios y asignándolos al vídeo...")
    try:
        # Usar slicing para recortar el audio de fondo
        audio_bg = audio_bg[0:duracion_total]
        audio_final = CompositeAudioClip([audio_principal, audio_bg])
        # Utilizar with_audio para asignar el audio al video
        video = video.with_audio(audio_final)
    except Exception as e:
        logging.exception("Error al combinar audios")
        return

    ruta_salida = os.path.join(carpeta, f"video_{nombre_carpeta}.mp4")
    logging.info(f"Guardando vídeo en: {ruta_salida}")
    try:
        video.write_videofile(ruta_salida, fps=24)
        logging.info("¡Vídeo creado exitosamente!")
    except Exception as e:
        logging.exception("Error al escribir el archivo de vídeo")

def procesar_ejecuciones(ruta_ejecucion="ejecucion"):
    logging.info(f"Iniciando procesamiento en la carpeta de ejecuciones: {ruta_ejecucion}")
    if not os.path.exists(ruta_ejecucion):
        logging.error(f"La carpeta '{ruta_ejecucion}' no existe.")
        return

    carpetas = [
        os.path.join(ruta_ejecucion, carpeta)
        for carpeta in os.listdir(ruta_ejecucion)
        if os.path.isdir(os.path.join(ruta_ejecucion, carpeta))
    ]

    if not carpetas:
        logging.warning("No se encontraron subcarpetas en la carpeta de ejecucion.")
        return

    for carpeta in sorted(carpetas):
        logging.info(f"Procesando carpeta: {carpeta}")
        crear_video_en_carpeta(carpeta)

if __name__ == "__main__":
    procesar_ejecuciones()
