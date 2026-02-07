import unittest
import sys
import os
import time

# Añadir el directorio raíz del proyecto al sys.path
# para permitir la importación de la 'libreria'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libreria.utils import format_timestamp

class TestUtils(unittest.TestCase):

    def test_format_timestamp_valid(self):
        """
        Prueba que format_timestamp formatea correctamente un timestamp válido.
        """
        # Un timestamp conocido: 1 de enero de 2024, 00:00:00 GMT
        ts = 1704067200
        expected_format = "2024-01-01 01:00:00" # Asumiendo zona horaria local GMT+1
        # Esto puede variar dependiendo de la zona horaria del sistema que ejecuta la prueba.
        # Para una prueba más robusta, se podría mockear la zona horaria.
        self.assertIn("2024-01-01", format_timestamp(ts))

    def test_format_timestamp_string(self):
        """
        Prueba que format_timestamp maneja un timestamp en formato de cadena.
        """
        ts = "1704067200"
        self.assertIn("2024-01-01", format_timestamp(ts))

    def test_format_timestamp_invalid(self):
        """
        Prueba que format_timestamp devuelve una cadena de fecha actual
        para una entrada inválida.
        """
        ts = "esto no es un timestamp"
        # La función debería devolver el tiempo actual, así que comprobamos que el año actual esté en el resultado.
        current_year = str(time.gmtime().tm_year)
        self.assertIn(current_year, format_timestamp(ts))
        
    def test_format_timestamp_none(self):
        """
        Prueba que format_timestamp devuelve una cadena de fecha actual
        para una entrada None.
        """
        ts = None
        current_year = str(time.gmtime().tm_year)
        self.assertIn(current_year, format_timestamp(ts))

if __name__ == '__main__':
    print("Ejecutando pruebas para libreria.utils...")
    unittest.main()

