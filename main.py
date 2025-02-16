import os
import logging
import io
import threading
import queue
import time
import gradio as gr
from utils.video_utils import crear_video_en_carpeta, procesar_ejecuciones, obtener_resolucion

# Configurar logging global
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    """Handler que envía logs a un queue."""
    def emit(self, record):
        try:
            msg = self.format(record)
            log_queue.put(msg)
        except Exception:
            self.handleError(record)

queue_handler = QueueHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
queue_handler.setFormatter(formatter)
logger.addHandler(queue_handler)

def listar_subcarpetas(ruta):
    """Devuelve las subcarpetas de la ruta dada."""
    if not os.path.exists(ruta):
        logger.error(f"La ruta {ruta} no existe.")
        return []
    subcarpetas = [d for d in os.listdir(ruta) if os.path.isdir(os.path.join(ruta, d))]
    logger.info(f"Subcarpetas encontradas en {ruta}: {subcarpetas}")
    return subcarpetas

def mostrar_explorador(ruta="data/ejecucion"):
    """
    Genera un texto en Markdown que muestra la estructura de carpetas de 'data/ejecucion'
    y explica cómo deben organizarse los archivos.
    """
    if not os.path.exists(ruta):
        return "La carpeta data/ejecucion no existe."
    md = "## Explorador de 'data/ejecucion'\n\n"
    subcarpetas = sorted(listar_subcarpetas(ruta))
    if not subcarpetas:
        md += "No se encontraron subcarpetas."
    else:
        for sub in subcarpetas:
            sub_path = os.path.join(ruta, sub)
            md += f"### Carpeta **{sub}**\n"
            md += f"- Debe contener un archivo de audio principal llamado `{sub}.wav`.\n"
            md += f"- Debe contener un archivo de música de fondo llamado `music_{sub}.mp3`.\n"
            md += f"- Debe tener una subcarpeta llamada `imagenes` que contenga las imágenes ordenadas alfabéticamente.\n\n"
    return md

def proceso_generacion(folder, resolucion):
    """Ejecuta la generación del video de forma síncrona."""
    base = "data/ejecucion"
    if folder == "Todos":
        resultado = procesar_ejecuciones(base, resolucion)
    else:
        folder_path = os.path.join(base, folder)
        resultado = crear_video_en_carpeta(folder_path, resolucion)
    return resultado

def generar_video_con_streaming(subfolder, resolucion_opcion, custom_width, custom_height):
    """
    Función generadora que ejecuta el proceso de generación de video en un hilo y 
    va enviando logs en tiempo real.
    """
    try:
        resolucion = obtener_resolucion(resolucion_opcion, custom_width, custom_height)
    except Exception as e:
        yield ("Error: " + str(e), "")
        return

    resultado_final = {"value": None}
    
    def worker():
        resultado_final["value"] = proceso_generacion(subfolder, resolucion)
    
    thread = threading.Thread(target=worker)
    thread.start()
    
    logs_acumulados = ""
    while thread.is_alive() or not log_queue.empty():
        try:
            while not log_queue.empty():
                msg = log_queue.get_nowait()
                logs_acumulados += msg + "\n"
        except Exception:
            pass
        # En cada iteración se envía el estado actual
        yield ("Procesando...", logs_acumulados)
        time.sleep(0.5)
    
    thread.join()
    try:
        while not log_queue.empty():
            msg = log_queue.get_nowait()
            logs_acumulados += msg + "\n"
    except Exception:
        pass

    if resultado_final["value"]:
        yield (f"Video generado en: {resultado_final['value']}", logs_acumulados)
    else:
        yield ("Error en la generación del video. Revisa los logs.", logs_acumulados)

def actualizar_visible(resolucion):
    """Actualiza la visibilidad de los inputs de resolución personalizada."""
    if resolucion == "Personalizado":
        return gr.update(visible=True), gr.update(visible=True)
    else:
        return gr.update(visible=False), gr.update(visible=False)

with gr.Blocks() as demo:
    gr.Markdown("# Generador de Video")
    gr.Markdown("""
**Instrucciones para armar los datos:**

- Cada carpeta de ejecución (por ejemplo, "1", "2", etc.) debe contener:
  - Un archivo de audio principal: `<número>.wav` (ej. `1.wav`).
  - Un archivo de música de fondo: `music_<número>.mp3` (ej. `music_1.mp3`).
  - Una carpeta llamada `imagenes` que contenga las imágenes ordenadas alfabéticamente.
    Estas imágenes serán procesadas para llenar la resolución de salida sin bordes.
""")
    
    with gr.Row():
        with gr.Column(scale=1):
            dropdown_folder = gr.Dropdown(choices=["Todos"] + listar_subcarpetas("data/ejecucion"),
                                            label="Selecciona una carpeta de ejecución")
            dropdown_resolucion = gr.Dropdown(choices=["1920x1080", "786x480", "Vertical", "Personalizado"],
                                              label="Selecciona la resolución de salida")
            with gr.Row():
                num_width = gr.Number(value=1920, label="Ancho personalizado (solo para 'Personalizado')", visible=False)
                num_height = gr.Number(value=1080, label="Alto personalizado (solo para 'Personalizado')", visible=False)
            btn = gr.Button("Generar Video", interactive=True)
            resultado_text = gr.Textbox(label="Resultado")
            logs_text = gr.Textbox(label="Logs del proceso", lines=20)
        with gr.Column(scale=1):
            explorer_md = gr.Markdown(mostrar_explorador(), label="Explorador de 'data/ejecucion'")
    
    # Asignar el evento change al dropdown de resolución
    dropdown_resolucion.change(fn=actualizar_visible, inputs=dropdown_resolucion, outputs=[num_width, num_height])
    # Al hacer click, deshabilitar el botón; la función generadora devolverá actualizaciones en tiempo real.
    btn.click(fn=generar_video_con_streaming, 
              inputs=[dropdown_folder, dropdown_resolucion, num_width, num_height], 
              outputs=[resultado_text, logs_text])
    
demo.launch(share=True)
