import os
import logging
import gradio as gr
from utils.video_utils import crear_video_en_carpeta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def generar_video(folder):
    """
    Función que recibe la ruta de una carpeta de ejecución y genera el video.
    Retorna la ruta del video generado o un mensaje de error.
    """
    salida = crear_video_en_carpeta(folder)
    if salida:
        return salida
    else:
        return "Error en la generación del video."

def listar_subcarpetas(ruta):
    """
    Lista las subcarpetas de la ruta especificada.
    """
    if not os.path.exists(ruta):
        return []
    return [d for d in os.listdir(ruta) if os.path.isdir(os.path.join(ruta, d))]

def interfaz_principal():
    base = "data/ejecucion"
    subcarpetas = listar_subcarpetas(base)
    
    def generar_video_interfaz(subfolder):
        folder_path = os.path.join(base, subfolder)
        salida = generar_video(folder_path)
        return salida
    
    iface = gr.Interface(
        fn=generar_video_interfaz,
        inputs=gr.Dropdown(choices=subcarpetas, label="Selecciona una carpeta de ejecución"),
        outputs=gr.Textbox(label="Ruta del video generado"),
        title="Generador de Video",
        description="Selecciona una carpeta de 'data/ejecucion' para generar el video."
    )
    iface.launch()

if __name__ == "__main__":
    interfaz_principal()