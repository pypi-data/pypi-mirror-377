"""
Módulo para verificar la versión actual del paquete
"""
import requests
import json
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def get_current_version() -> str:
    """Obtener la versión actual del paquete"""
    try:
        # Intentar obtener la versión desde el paquete instalado usando importlib.metadata
        try:
            from importlib.metadata import version
            return version("ia-agent-dotnet")
        except ImportError:
            # Fallback para Python < 3.8
            import pkg_resources
            return pkg_resources.get_distribution("ia-agent-dotnet").version
    except Exception:
        # Fallback: leer desde setup.py o pyproject.toml
        try:
            with open("setup.py", "r", encoding="utf-8") as f:
                content = f.read()
                for line in content.split("\n"):
                    if "version=" in line:
                        version = line.split("version=")[1].strip().strip('"').strip("'")
                        return version
        except Exception:
            return "0.0.0"

def get_latest_version() -> Optional[str]:
    """Obtener la última versión disponible en PyPI"""
    try:
        response = requests.get(
            "https://pypi.org/pypi/ia-agent-dotnet/json",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
    except Exception as e:
        console.print(f"[dim]No se pudo verificar la versión más reciente: {e}[/dim]")
    return None

def compare_versions(current: str, latest: str) -> int:
    """Comparar dos versiones semánticas
    Retorna: -1 si current < latest, 0 si son iguales, 1 si current > latest
    """
    def version_tuple(version: str):
        return tuple(map(int, version.split(".")))
    
    try:
        current_tuple = version_tuple(current)
        latest_tuple = version_tuple(latest)
        
        if current_tuple < latest_tuple:
            return -1
        elif current_tuple > latest_tuple:
            return 1
        else:
            return 0
    except Exception:
        return 0

def check_version_update() -> bool:
    """Verificar si hay una actualización disponible"""
    current_version = get_current_version()
    latest_version = get_latest_version()
    
    if not latest_version:
        return False
    
    comparison = compare_versions(current_version, latest_version)
    
    if comparison < 0:  # current < latest
        show_update_message(current_version, latest_version)
        return True
    
    return False

def show_update_message(current_version: str, latest_version: str):
    """Mostrar mensaje de actualización disponible"""
    update_text = f"""[bold yellow]🔄 Actualización Disponible[/bold yellow]

[bold]Versión actual:[/bold] {current_version}
[bold]Última versión:[/bold] [green]{latest_version}[/green]

[bold cyan]Para actualizar ejecuta:[/bold cyan]
[bold]pip install --upgrade ia-agent-dotnet[/bold]

[dim]Las actualizaciones incluyen mejoras de rendimiento, nuevas funcionalidades y correcciones de errores.[/dim]"""
    
    console.print(Panel(
        update_text,
        title="[bold blue]Actualización Recomendada[/bold blue]",
        border_style="yellow",
        padding=(1, 2)
    ))
    console.print()  # Línea en blanco
