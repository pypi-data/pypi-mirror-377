"""
Módulo para validar la configuración de API keys
"""
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from config.global_config import GlobalConfigManager

console = Console()

class ConfigValidator:
    """Validador de configuración de API keys"""
    
    def __init__(self):
        self.config_manager = GlobalConfigManager()
    
    def check_api_configuration(self) -> Dict[str, Any]:
        """Verificar la configuración de API keys"""
        config = self.config_manager.get_config()
        
        results = {
            "has_config": False,
            "provider": None,
            "api_key_configured": False,
            "config_valid": False,
            "missing_fields": []
        }
        
        if not config:
            return results
        
        results["has_config"] = True
        results["provider"] = getattr(config, "ai_provider", "unknown")
        
        # Verificar según el proveedor
        if results["provider"] == "deepseek":
            api_key = getattr(config, "deepseek_api_key", None)
            if self._is_valid_api_key(api_key, "deepseek"):
                results["api_key_configured"] = True
            else:
                results["missing_fields"].append("deepseek_api_key")
        
        elif results["provider"] == "gemini":
            api_key = getattr(config, "gemini_api_key", None)
            if self._is_valid_api_key(api_key, "gemini"):
                results["api_key_configured"] = True
            else:
                results["missing_fields"].append("gemini_api_key")
        
        elif results["provider"] == "openai":
            api_key = getattr(config, "openai_api_key", None)
            if self._is_valid_api_key(api_key, "openai"):
                results["api_key_configured"] = True
            else:
                results["missing_fields"].append("openai_api_key")
        
        # La configuración es válida si tiene proveedor y API key
        results["config_valid"] = (
            results["provider"] != "unknown" and 
            results["api_key_configured"]
        )
        
        return results
    
    def show_config_status(self, config_status: Dict[str, Any]):
        """Mostrar el estado de la configuración"""
        if config_status["config_valid"]:
            self._show_valid_config(config_status)
        else:
            self._show_invalid_config(config_status)
    
    def _show_valid_config(self, config_status: Dict[str, Any]):
        """Mostrar configuración válida"""
        provider_name = {
            "deepseek": "DeepSeek",
            "gemini": "Google Gemini",
            "openai": "OpenAI"
        }.get(config_status["provider"], config_status["provider"])
        
        status_text = f"""[bold green]✅ Configuración de IA Válida[/bold green]

[bold]Proveedor:[/bold] {provider_name}
[bold]Estado:[/bold] [green]Configurado correctamente[/green]

[dim]Puedes usar todas las funcionalidades del agente.[/dim]"""
        
        console.print(Panel(
            status_text,
            title="[bold blue]Estado de Configuración[/bold blue]",
            border_style="green",
            padding=(1, 2),
            expand=False
        ))
        console.print()
    
    def _show_invalid_config(self, config_status: Dict[str, Any]):
        """Mostrar configuración inválida o faltante"""
        if not config_status["has_config"]:
            self._show_no_config()
        elif not config_status["api_key_configured"]:
            self._show_missing_api_key(config_status)
        else:
            self._show_unknown_provider()
    
    def _show_no_config(self):
        """Mostrar cuando no hay configuración"""
        config_text = f"""[bold red]❌ Configuración de IA No Encontrada[/bold red]

[bold yellow]Para usar las funcionalidades del agente necesitas configurar una API key.[/bold yellow]

[bold cyan]Para configurar ejecuta:[/bold cyan]
[bold]ia-agent-config[/bold]

[dim]Esto te permitirá seleccionar el proveedor de IA y configurar tu API key.[/dim]"""
        
        console.print(Panel(
            config_text,
            title="[bold red]Configuración Requerida[/bold red]",
            border_style="red",
            padding=(1, 2),
            expand=False
        ))
        console.print()
    
    def _show_missing_api_key(self, config_status: Dict[str, Any]):
        """Mostrar cuando falta la API key"""
        provider_name = {
            "deepseek": "DeepSeek",
            "gemini": "Google Gemini", 
            "openai": "OpenAI"
        }.get(config_status["provider"], config_status["provider"])
        
        config_text = f"""[bold red]❌ API Key No Configurada[/bold red]

[bold]Proveedor seleccionado:[/bold] {provider_name}
[bold red]API Key:[/bold red] [red]No configurada[/red]

[bold cyan]Para configurar tu API key ejecuta:[/bold cyan]
[bold]ia-agent-config[/bold]

[dim]Necesitas una API key válida para usar las funcionalidades del agente.[/dim]"""
        
        console.print(Panel(
            config_text,
            title="[bold red]API Key Requerida[/bold red]",
            border_style="red",
            padding=(1, 2),
            expand=False
        ))
        console.print()
    
    def _show_unknown_provider(self):
        """Mostrar cuando el proveedor es desconocido"""
        config_text = f"""[bold red]❌ Proveedor de IA Desconocido[/bold red]

[bold yellow]El proveedor configurado no es válido.[/bold yellow]

[bold cyan]Para reconfigurar ejecuta:[/bold cyan]
[bold]ia-agent-config[/bold]

[dim]Esto te permitirá seleccionar un proveedor válido y configurar tu API key.[/dim]"""
        
        console.print(Panel(
            config_text,
            title="[bold red]Configuración Inválida[/bold red]",
            border_style="red",
            padding=(1, 2),
            expand=False
        ))
        console.print()
    
    def _is_valid_api_key(self, api_key: Optional[str], provider: str) -> bool:
        """Verificar si una API key es válida (no es placeholder)"""
        if not api_key or not api_key.strip():
            return False
        
        # Lista de placeholders comunes
        placeholders = [
            "your_deepseek_api_key_here",
            "your_gemini_api_key_here", 
            "your_openai_api_key_here",
            "sk-your-key-here",
            "AIza-your-key-here",
            "your_api_key",
            "api_key_here",
            "replace_with_your_key",
            "your_key_here"
        ]
        
        # Verificar si es un placeholder
        if api_key.strip() in placeholders:
            return False
        
        # Verificar longitud mínima (las API keys reales suelen ser más largas)
        if len(api_key.strip()) < 20:
            return False
        
        # Verificar patrones específicos por proveedor
        if provider == "deepseek":
            # Las API keys de DeepSeek suelen empezar con "sk-"
            return api_key.strip().startswith("sk-")
        elif provider == "gemini":
            # Las API keys de Gemini suelen empezar con "AIza"
            return api_key.strip().startswith("AIza")
        elif provider == "openai":
            # Las API keys de OpenAI suelen empezar con "sk-"
            return api_key.strip().startswith("sk-")
        
        return True
    
    def is_config_valid(self) -> bool:
        """Verificar si la configuración es válida"""
        config_status = self.check_api_configuration()
        return config_status["config_valid"]
