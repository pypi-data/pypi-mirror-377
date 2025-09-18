#!/usr/bin/env python3
"""
CLI de configuración para IA Agent
IA Agent para Generación de Pruebas Unitarias .NET
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from utils.logging import get_logger
from config.global_config import global_config_manager, GlobalConfig

console = Console()
logger = get_logger("config-cli")


class ConfigCLI:
    """CLI para configuración de API keys y proveedores"""
    
    def __init__(self):
        self.config_manager = global_config_manager
        self.providers = {
            "1": {
                "name": "DeepSeek",
                "key": "DEEPSEEK_API_KEY",
                "model": "deepseek-coder",
                "provider": "deepseek",
                "description": "Especializado en programación, más económico",
                "url": "https://platform.deepseek.com/"
            },
            "2": {
                "name": "Gemini Flash",
                "key": "GEMINI_API_KEY", 
                "model": "gemini-2.5-flash",
                "provider": "gemini",
                "description": "Google AI 2.5, rápido y eficiente para análisis general",
                "url": "https://makersuite.google.com/app/apikey"
            },
            "3": {
                "name": "Gemini Pro",
                "key": "GEMINI_API_KEY", 
                "model": "gemini-2.5-pro",
                "provider": "gemini",
                "description": "Google AI 2.5 Pro, más potente para tareas complejas",
                "url": "https://makersuite.google.com/app/apikey"
            },
            "4": {
                "name": "OpenAI",
                "key": "OPENAI_API_KEY",
                "model": "gpt-4",
                "provider": "openai",
                "description": "Estándar de la industria, más caro",
                "url": "https://platform.openai.com/api-keys"
            }
        }
    
    def show_welcome(self):
        """Mostrar mensaje de bienvenida"""
        welcome_text = Text()
        welcome_text.append("🔧 ", style="bold blue")
        welcome_text.append("Configuración de IA Agent", style="bold")
        welcome_text.append("\n\nConfigura tu proveedor de IA y API key para comenzar a usar el sistema.")
        
        console.print(Panel(welcome_text, title="IA Agent - Configuración", border_style="blue"))
    
    def show_providers(self):
        """Mostrar proveedores disponibles"""
        table = Table(title="🤖 Proveedores de IA Disponibles")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Proveedor", style="magenta")
        table.add_column("Modelo", style="green")
        table.add_column("Descripción", style="white")
        
        for provider_id, provider in self.providers.items():
            table.add_row(
                provider_id,
                provider["name"],
                provider["model"],
                provider["description"]
            )
        
        console.print(table)
        console.print()
    
    def get_provider_choice(self) -> str:
        """Obtener elección del proveedor"""
        while True:
            choice = Prompt.ask(
                "Selecciona un proveedor (1-4)",
                choices=["1", "2", "3", "4"],
                default="1"
            )
            
            if choice in self.providers:
                return choice
            
            console.print("❌ Opción inválida. Por favor selecciona 1, 2 o 3.", style="red")
    
    def get_api_key(self, provider_name: str) -> str:
        """Obtener API key del usuario"""
        console.print(f"\n🔑 Configuración de API Key para {provider_name}")
        console.print("💡 Tu API key se guardará globalmente para todos tus proyectos")
        
        while True:
            api_key = Prompt.ask(
                f"Ingresa tu API key de {provider_name}",
                password=True
            )
            
            if api_key and len(api_key) > 10:
                return api_key
            
            console.print("❌ API key inválida. Debe tener al menos 10 caracteres.", style="red")
    
    def show_provider_info(self, provider_id: str):
        """Mostrar información del proveedor seleccionado"""
        provider = self.providers[provider_id]
        
        info_text = Text()
        info_text.append(f"Proveedor: ", style="bold")
        info_text.append(f"{provider['name']}\n", style="cyan")
        info_text.append(f"Modelo: ", style="bold")
        info_text.append(f"{provider['model']}\n", style="green")
        info_text.append(f"Descripción: ", style="bold")
        info_text.append(f"{provider['description']}\n\n", style="white")
        info_text.append("Para obtener tu API key, visita:\n", style="bold")
        info_text.append(f"{provider['url']}", style="blue underline")
        
        console.print(Panel(info_text, title=f"📋 Información de {provider['name']}", border_style="green"))
    
    def save_config(self, provider_id: str, api_key: str):
        """Guardar configuración globalmente"""
        provider = self.providers[provider_id]
        
        # Actualizar configuración global
        success = self.config_manager.update_config(
            **{provider["key"].lower(): api_key},
            ai_provider=provider["provider"],
            ai_model=provider["model"],
            ai_temperature=0.1,
            ai_max_tokens=4000
        )
        
        if success:
            config_info = self.config_manager.get_config_info()
            console.print(f"✅ Configuración guardada globalmente en: {config_info['config_file']}", style="green")
        else:
            console.print("❌ Error al guardar configuración global", style="red")
    
    def test_configuration(self, provider_id: str, api_key: str) -> bool:
        """Probar la configuración"""
        provider = self.providers[provider_id]
        
        console.print(f"\n🧪 Probando configuración de {provider['name']}...")
        
        try:
            # Importar y probar el proveedor
            if provider_id == "1":  # DeepSeek
                from ai.llm_manager import DeepSeekLLM
                llm = DeepSeekLLM(api_key=api_key, model=provider["model"])
                response = llm.invoke("Hola, ¿puedes responder con 'OK'?")
                if "OK" in response.content or "ok" in response.content.lower():
                    return True
                    
            elif provider_id == "2":  # Gemini
                from ai.llm_manager import GeminiLLM
                llm = GeminiLLM(api_key=api_key, model=provider["model"])
                response = llm.invoke("Hola, ¿puedes responder con 'OK'?")
                if "OK" in response.content or "ok" in response.content.lower():
                    return True
                    
            elif provider_id == "3":  # OpenAI
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(api_key=api_key, model=provider["model"])
                response = llm.invoke("Hola, ¿puedes responder con 'OK'?")
                if "OK" in response.content or "ok" in response.content.lower():
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error al probar configuración: {e}")
            return False
    
    def show_success(self, provider_name: str):
        """Mostrar mensaje de éxito"""
        success_text = Text()
        success_text.append("🎉 ", style="bold green")
        success_text.append("¡Configuración completada exitosamente!\n\n", style="bold green")
        success_text.append(f"Proveedor: ", style="bold")
        success_text.append(f"{provider_name}\n", style="cyan")
        success_text.append("Estado: ", style="bold")
        success_text.append("✅ Configurado y funcionando\n\n", style="green")
        success_text.append("Ahora puedes usar el sistema en cualquier proyecto:\n", style="bold")
        success_text.append("• ia-agent --help\n", style="blue")
        success_text.append("• ia-agent analyze --project ./mi-proyecto\n", style="blue")
        success_text.append("• ia-agent generate --file ./Controllers/UserController.cs\n\n", style="blue")
        success_text.append("💡 La configuración es global y se aplica a todos tus proyectos", style="yellow")
        
        console.print(Panel(success_text, title="✅ Configuración Exitosa", border_style="green"))
    
    def show_current_config(self):
        """Mostrar configuración actual"""
        config_info = self.config_manager.get_config_info()
        
        config_text = Text()
        config_text.append("📊 ", style="bold blue")
        config_text.append("Configuración Actual de IA Agent\n\n", style="bold blue")
        config_text.append("Archivo de configuración: ", style="bold")
        config_text.append(f"{config_info['config_file']}\n", style="cyan")
        config_text.append("Proveedor: ", style="bold")
        config_text.append(f"{config_info['ai_provider']}\n", style="green")
        config_text.append("Modelo: ", style="bold")
        config_text.append(f"{config_info['ai_model']}\n", style="green")
        config_text.append("Estado: ", style="bold")
        config_text.append("✅ Configurado\n" if config_info['is_configured'] else "❌ No configurado\n", 
                          style="green" if config_info['is_configured'] else "red")
        
        console.print(Panel(config_text, title="🔧 Configuración Actual", border_style="blue"))
    
    def run(self):
        """Ejecutar CLI de configuración"""
        try:
            self.show_welcome()
            self.show_providers()
            
            # Verificar si ya existe configuración global
            if self.config_manager.is_configured():
                config_info = self.config_manager.get_config_info()
                console.print(f"Ya existe configuración global para {config_info['ai_provider']}")
                if not Confirm.ask("¿Deseas reconfigurar?"):
                    console.print("Configuración cancelada.", style="yellow")
                    return
            
            # Obtener elección del proveedor
            provider_id = self.get_provider_choice()
            provider = self.providers[provider_id]
            
            # Mostrar información del proveedor
            self.show_provider_info(provider_id)
            
            # Obtener API key
            api_key = self.get_api_key(provider["name"])
            
            # Probar configuración
            if Confirm.ask("¿Deseas probar la configuración antes de guardar?"):
                if self.test_configuration(provider_id, api_key):
                    console.print("✅ Configuración probada exitosamente!", style="green")
                else:
                    console.print("❌ Error en la configuración. Verifica tu API key.", style="red")
                    if not Confirm.ask("¿Deseas continuar de todos modos?"):
                        console.print("Configuración cancelada.", style="yellow")
                        return
            
            # Guardar configuración
            self.save_config(provider_id, api_key)
            
            # Mostrar éxito
            self.show_success(provider["name"])
            
        except KeyboardInterrupt:
            console.print("\n\nConfiguración cancelada por el usuario.", style="yellow")
        except Exception as e:
            logger.error(f"Error en configuración: {e}")
            console.print(f"❌ Error: {e}", style="red")


def main():
    """Función principal"""
    import sys
    
    cli = ConfigCLI()
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status" or sys.argv[1] == "-s":
            cli.show_current_config()
            return
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            help_text = Text()
            help_text.append("🔧 ", style="bold blue")
            help_text.append("IA Agent - Configuración\n\n", style="bold blue")
            help_text.append("Uso:\n", style="bold")
            help_text.append("  ia-agent-config          Configurar el agente interactivamente\n", style="white")
            help_text.append("  ia-agent-config --status Mostrar configuración actual\n", style="white")
            help_text.append("  ia-agent-config --help   Mostrar esta ayuda\n\n", style="white")
            help_text.append("La configuración se guarda globalmente y se aplica a todos tus proyectos.", style="yellow")
            console.print(Panel(help_text, title="Ayuda", border_style="blue"))
            return
    
    # Ejecutar configuración interactiva
    cli.run()


if __name__ == "__main__":
    main()
