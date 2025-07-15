#!/usr/bin/env python3
"""
Script principal para ejecutar los seeders desde la raíz del proyecto
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar directamente desde el archivo específico
from seeders.main_seeder import main

if __name__ == "__main__":
    main()