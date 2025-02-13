import numpy as np
from PIL import Image
import logging

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
    # Redimensionar usando LANCZOS (en Pillow 10+)
    im_resized = im.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    fondo = Image.new("RGB", tamano_final, (0, 0, 0))
    x_offset = (tamano_final[0] - nuevo_ancho) // 2
    y_offset = (tamano_final[1] - nuevo_alto) // 2
    fondo.paste(im_resized, (x_offset, y_offset))
    return np.array(fondo)
