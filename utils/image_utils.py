import numpy as np
from PIL import Image
import logging

def procesar_imagen(ruta_imagen, tamano_final=(1920, 1080)):
    """
    Abre la imagen usando Pillow, la redimensiona en modo "fill" para que cubra completamente
    el tamaño final (tamano_final) y luego recorta el exceso para centrar la imagen.
    
    Esto asegura que, por ejemplo:
      - En resoluciones horizontales, la imagen se escale de modo que no queden bordes negros y se recorte
        (si es necesario) para llenar la pantalla.
      - En resoluciones verticales, la altura de la imagen se ajusta al valor final y se recortan los laterales.
      
    Devuelve un arreglo NumPy que se puede usar para crear un ImageClip.
    """
    try:
        im = Image.open(ruta_imagen).convert("RGB")
    except Exception as e:
        logging.exception(f"No se pudo abrir la imagen: {ruta_imagen}")
        return None

    original_width, original_height = im.size
    final_width, final_height = tamano_final

    # Calcular los factores de escala para que la imagen cubra completamente el área deseada (modo fill)
    scale_w = final_width / original_width
    scale_h = final_height / original_height
    scale = max(scale_w, scale_h)

    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    
    # Redimensionar la imagen usando LANCZOS (alta calidad)
    im_resized = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Calcular el área central para recortar
    left = (new_width - final_width) // 2
    top = (new_height - final_height) // 2
    right = left + final_width
    bottom = top + final_height
    
    im_cropped = im_resized.crop((left, top, right, bottom))
    return np.array(im_cropped)
