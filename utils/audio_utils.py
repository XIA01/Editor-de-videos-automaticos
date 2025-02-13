import os
import logging
import tempfile
from pydub import AudioSegment
from moviepy.audio.io.AudioFileClip import AudioFileClip

def cargar_audio_principal(ruta_audio: str):
    """
    Carga el audio principal usando MoviePy.
    """
    try:
        return AudioFileClip(ruta_audio)
    except Exception as e:
        logging.exception(f"Error al cargar el audio principal: {ruta_audio}")
        return None

def procesar_audio_fondo(ruta_audio: str):
    """
    Procesa el audio de fondo con PyDub para ajustar el volumen al 20%.
    Exporta a un archivo temporal y lo carga con MoviePy.
    """
    try:
        audio = AudioSegment.from_file(ruta_audio)
        audio = audio - 14  # Reducción aproximada de 14 dB
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_file.close()
        audio.export(tmp_file.name, format="mp3")
        return AudioFileClip(tmp_file.name)
    except Exception as e:
        logging.exception(f"Error al procesar el audio de fondo: {ruta_audio}")
        return None
