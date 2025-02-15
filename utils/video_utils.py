import os
import logging
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.VideoClip import ImageClip
from utils.image_utils import procesar_imagen
from utils.audio_utils import cargar_audio_principal, procesar_audio_fondo

def obtener_resolucion(opcion, custom_width=None, custom_height=None):
    """
    Dada una opción de resolución (string), devuelve una tupla (ancho, alto).
    Opciones predefinidas:
      - "1920x1080" -> (1920, 1080)
      - "786x480"   -> (786, 480)
      - "Vertical"  -> (720, 1280)
      - "Personalizado" -> (custom_width, custom_height) (si se proporcionan)
    """
    if opcion == "1920x1080":
        return (1920, 1080)
    elif opcion == "786x480":
        return (786, 480)
    elif opcion == "Vertical":
        return (720, 1280)
    elif opcion == "Personalizado":
        if custom_width is not None and custom_height is not None:
            return (int(custom_width), int(custom_height))
        else:
            raise ValueError("Debe proporcionar custom_width y custom_height para opción 'Personalizado'")
    else:
        raise ValueError("Opción de resolución desconocida")

def crear_video_en_carpeta(carpeta, resolucion=(1920,1080)):
    logging.info(f"Iniciando procesamiento de la carpeta: {carpeta}")

    ruta_imagenes = os.path.join(carpeta, "imagenes")
    if not os.path.exists(ruta_imagenes):
        logging.error(f"La carpeta de imágenes no existe: {ruta_imagenes}")
        return None

    try:
        lista_imagenes = sorted(
            archivo for archivo in os.listdir(ruta_imagenes)
            if archivo.lower().endswith((".png", ".jpg", ".jpeg"))
        )
    except Exception as e:
        logging.exception("Error al listar imágenes en la carpeta de imágenes")
        return None

    logging.info(f"Se encontraron {len(lista_imagenes)} imágenes en {ruta_imagenes}")

    nombre = os.path.basename(carpeta)
    ruta_audio_principal = os.path.join(carpeta, f"{nombre}.wav")
    ruta_audio_bg = os.path.join(carpeta, f"music_{nombre}.mp3")

    if not os.path.exists(ruta_audio_principal):
        logging.error(f"Audio principal no encontrado: {ruta_audio_principal}")
        return None
    if not os.path.exists(ruta_audio_bg):
        logging.error(f"Audio de fondo no encontrado: {ruta_audio_bg}")
        return None

    logging.info("Cargando audio principal...")
    audio_principal = cargar_audio_principal(ruta_audio_principal)
    if audio_principal is None:
        return None

    logging.info("Procesando audio de fondo...")
    audio_bg = procesar_audio_fondo(ruta_audio_bg)
    if audio_bg is None:
        return None

    duracion_total = audio_principal.duration
    logging.info(f"Duración total del audio principal: {duracion_total} segundos")

    num_imagenes = len(lista_imagenes)
    if num_imagenes == 0:
        logging.error("No se encontraron imágenes para procesar")
        return None

    duracion_imagen = duracion_total / num_imagenes
    logging.info(f"Cada imagen tendrá una duración de: {duracion_imagen} segundos")

    clips = []
    for idx, imagen in enumerate(lista_imagenes, start=1):
        ruta = os.path.join(ruta_imagenes, imagen)
        logging.info(f"Procesando imagen {idx}/{num_imagenes}: {ruta}")
        img_array = None
        try:
            img_array = __import__("utils.image_utils", fromlist=["procesar_imagen"]).procesar_imagen(ruta, tamano_final=resolucion)
        except Exception as e:
            logging.exception(f"Error al procesar la imagen: {ruta}")
            continue
        if img_array is None:
            continue
        clip = ImageClip(img_array, duration=duracion_imagen)
        clips.append(clip)

    if not clips:
        logging.error("No se pudieron procesar clips de imagen correctamente.")
        return None

    logging.info("Concatenando clips de imagen...")
    try:
        video = concatenate_videoclips(clips, method="compose")
    except Exception as e:
        logging.exception("Error al concatenar clips de imagen")
        return None

    logging.info("Ajustando audios y asignándolos al vídeo...")
    try:
        audio_bg = audio_bg[0:duracion_total]
        audio_final = CompositeAudioClip([audio_principal, audio_bg])
        video = video.with_audio(audio_final)
    except Exception as e:
        logging.exception("Error al combinar audios")
        return None

    salida = os.path.join(carpeta, f"video_{nombre}.mp4")
    logging.info(f"Guardando vídeo en: {salida}")
    try:
        video.write_videofile(salida, fps=24)
        logging.info("¡Vídeo creado exitosamente!")
        return salida
    except Exception as e:
        logging.exception("Error al escribir el archivo de vídeo")
        return None

def procesar_ejecuciones(ruta_ejecucion, resolucion=(1920,1080)):
    if not os.path.exists(ruta_ejecucion):
        logging.error(f"La carpeta '{ruta_ejecucion}' no existe.")
        return None
    carpetas = [
        os.path.join(ruta_ejecucion, carpeta)
        for carpeta in os.listdir(ruta_ejecucion)
        if os.path.isdir(os.path.join(ruta_ejecucion, carpeta))
    ]
    if not carpetas:
        logging.warning("No se encontraron subcarpetas en la carpeta de ejecucion.")
        return None
    resultados = {}
    for carpeta in sorted(carpetas):
        logging.info(f"Procesando carpeta: {carpeta}")
        salida = crear_video_en_carpeta(carpeta, resolucion)
        if salida:
            resultados[carpeta] = salida
    return resultados
