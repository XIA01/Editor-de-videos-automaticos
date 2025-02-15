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
    gr.Markdown("Selecciona una carpeta de `data/ejecucion` y la resolución de salida para generar el video. Los logs se mostrarán en tiempo real.")

    with gr.Row():
        dropdown_folder = gr.Dropdown(choices=["Todos"] + listar_subcarpetas("data/ejecucion"),
                                        label="Selecciona una carpeta de ejecución")
    with gr.Row():
        dropdown_resolucion = gr.Dropdown(choices=["1920x1080", "786x480", "Vertical", "Personalizado"],
                                          label="Selecciona la resolución de salida")
    with gr.Row():
        num_width = gr.Number(value=1920, label="Ancho personalizado (solo para 'Personalizado')", visible=False)
        num_height = gr.Number(value=1080, label="Alto personalizado (solo para 'Personalizado')", visible=False)
    btn = gr.Button("Generar Video")
    resultado_text = gr.Textbox(label="Resultado")
    logs_text = gr.Textbox(label="Logs del proceso", lines=20)

    dropdown_resolucion.change(fn=actualizar_visible, inputs=dropdown_resolucion, outputs=[num_width, num_height])
    # Se elimina el parámetro stream=True aquí.
    btn.click(fn=generar_video_con_streaming, 
              inputs=[dropdown_folder, dropdown_resolucion, num_width, num_height], 
              outputs=[resultado_text, logs_text])

demo.launch(share=True)
