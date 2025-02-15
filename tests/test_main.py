import unittest
import os
from utils.video_utils import procesar_ejecuciones, obtener_resolucion

class TestVideoPipeline(unittest.TestCase):
    def test_obtener_resolucion(self):
        self.assertEqual(obtener_resolucion("1920x1080"), (1920, 1080))
        self.assertEqual(obtener_resolucion("786x480"), (786, 480))
        self.assertEqual(obtener_resolucion("Vertical"), (720, 1280))
        with self.assertRaises(ValueError):
            obtener_resolucion("Personalizado")
    
    def test_procesar_ejecuciones(self):
        ruta = "data/ejecucion"
        # Esta prueba asume que la carpeta existe
        self.assertTrue(os.path.exists(ruta))
        resultados = procesar_ejecuciones(ruta, resolucion=(1920,1080))
        self.assertIsInstance(resultados, dict)

if __name__ == '__main__':
    unittest.main()
