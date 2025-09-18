"""
Punto de entrada principal para el CLI
IA Agent para Generación de Pruebas Unitarias .NET
"""

import sys
import os
import asyncio
from pathlib import Path

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.interactive_cli import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n¡Hasta luego!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
