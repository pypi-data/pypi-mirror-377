"""
Interfaz CLI con capacidades multi-agente
IA Agent para Generación de Pruebas Unitarias .NET
"""

import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.tree import Tree

from agents.analysis_agent import analysis_agent
from agents.generation_agent import generation_agent
from agents.validation_agent import validation_agent
from agents.optimization_agent import optimization_agent
from agents.coordinator_agent import coordinator_agent
from multi_agent.autogen_collaboration import multi_agent_collaboration
from multi_agent.shared_memory import SharedMemory
from utils.config import Config, get_config
from utils.logging import get_logger, setup_logging

logger = get_logger("multi-agent-cli")
console = Console()


class MultiAgentCLI:
    """Interfaz CLI con capacidades multi-agente"""
    
    def __init__(self):
        self.config = get_config()
        self.shared_memory = SharedMemory()
        self.collaboration = multi_agent_collaboration
        self.console = console
        
        # Estado de la sesión
        self.current_project_path = None
        self.current_session_id = None
        self.agents_initialized = False
        
        self.logger = logger
    
    def initialize(self) -> bool:
        """Inicializar CLI y agentes"""
        try:
            self.console.print(Panel.fit(
                "[bold blue]IA Agent para Generación de Pruebas Unitarias .NET[/bold blue]\n"
                "[dim]Sistema Multi-Agente con LangChain y AutoGen[/dim]",
                title="🚀 Inicializando Sistema"
            ))
            
            # Configurar logging
            setup_logging(level=self.config.agent.log_level)
            
            # Inicializar colaboración multi-agente
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Inicializando agentes...", total=None)
                
                success = self.collaboration.initialize()
                if not success:
                    self.console.print("[red]Error al inicializar sistema de colaboración[/red]")
                    return False
                
                progress.update(task, description="✅ Sistema inicializado")
            
            self.agents_initialized = True
            self.console.print("[green]✅ Sistema multi-agente inicializado exitosamente[/green]")
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error al inicializar CLI: {e}[/red]")
            self.logger.error(f"Error al inicializar CLI: {e}")
            return False
    
    def show_main_menu(self):
        """Mostrar menú principal"""
        while True:
            self.console.clear()
            self.console.print(Panel.fit(
                "[bold blue]IA Agent para Generación de Pruebas Unitarias .NET[/bold blue]\n"
                "[dim]Sistema Multi-Agente con LangChain y AutoGen[/dim]",
                title="🏠 Menú Principal"
            ))
            
            # Mostrar estado actual
            self._show_current_status()
            
            # Mostrar opciones
            options = [
                "1. Análisis de Proyecto .NET",
                "2. Generación de Pruebas Unitarias",
                "3. Validación de Código",
                "4. Optimización de Pruebas",
                "5. Colaboración Multi-Agente",
                "6. Gestión de Memoria",
                "7. Configuración",
                "8. Salir"
            ]
            
            for option in options:
                self.console.print(f"  {option}")
            
            choice = Prompt.ask("\n[bold]Selecciona una opción[/bold]", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                self._handle_project_analysis()
            elif choice == "2":
                self._handle_test_generation()
            elif choice == "3":
                self._handle_code_validation()
            elif choice == "4":
                self._handle_test_optimization()
            elif choice == "5":
                self._handle_multi_agent_collaboration()
            elif choice == "6":
                self._handle_memory_management()
            elif choice == "7":
                self._handle_configuration()
            elif choice == "8":
                if Confirm.ask("¿Estás seguro de que quieres salir?"):
                    self._shutdown()
                    break
    
    def _show_current_status(self):
        """Mostrar estado actual del sistema"""
        status_table = Table(title="Estado del Sistema")
        status_table.add_column("Componente", style="cyan")
        status_table.add_column("Estado", style="green")
        status_table.add_column("Detalles", style="dim")
        
        # Estado de agentes
        status_table.add_row("Agentes", "✅ Inicializados" if self.agents_initialized else "❌ No inicializados", 
                           f"{len(self.collaboration.autogen_agents)} agentes disponibles")
        
        # Estado de proyecto
        project_status = "✅ Configurado" if self.current_project_path else "❌ No configurado"
        project_details = self.current_project_path or "Ningún proyecto seleccionado"
        status_table.add_row("Proyecto", project_status, project_details)
        
        # Estado de sesión
        session_status = "✅ Activa" if self.current_session_id else "❌ Inactiva"
        session_details = self.current_session_id or "Ninguna sesión activa"
        status_table.add_row("Sesión", session_status, session_details)
        
        # Estado de memoria
        memory_stats = self.shared_memory.get_memory_stats()
        memory_status = "✅ Activa" if memory_stats.get("total_entries", 0) > 0 else "❌ Vacía"
        memory_details = f"{memory_stats.get('total_entries', 0)} entradas"
        status_table.add_row("Memoria", memory_status, memory_details)
        
        self.console.print(status_table)
        self.console.print()
    
    def _handle_project_analysis(self):
        """Manejar análisis de proyecto"""
        self.console.print(Panel.fit("Análisis de Proyecto .NET", title="🔍 Análisis"))
        
        # Solicitar ruta del proyecto
        project_path = Prompt.ask("Ruta del proyecto .NET", default=self.current_project_path or ".")
        
        if not os.path.exists(project_path):
            self.console.print("[red]La ruta del proyecto no existe[/red]")
            return
        
        # Configurar proyecto actual
        self.current_project_path = project_path
        self.shared_memory.set_project_context(
            project_id=f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            project_name=Path(project_path).name,
            project_path=project_path,
            framework="xunit"
        )
        
        # Ejecutar análisis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analizando proyecto...", total=None)
            
            try:
                # Usar agente analista
                result = analysis_agent.process_task(
                    type('Task', (), {
                        'task_id': f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'description': f"Analizar proyecto en {project_path}",
                        'priority': 1,
                        'status': 'pending'
                    })()
                )
                
                progress.update(task, description="✅ Análisis completado")
                
                # Mostrar resultados
                self._display_analysis_results(result)
                
            except Exception as e:
                progress.update(task, description="❌ Error en análisis")
                self.console.print(f"[red]Error durante el análisis: {e}[/red]")
    
    def _handle_test_generation(self):
        """Manejar generación de pruebas"""
        self.console.print(Panel.fit("Generación de Pruebas Unitarias", title="⚡ Generación"))
        
        if not self.current_project_path:
            self.console.print("[red]Primero debes analizar un proyecto[/red]")
            return
        
        # Solicitar tipo de generación
        generation_type = Prompt.ask(
            "Tipo de generación",
            choices=["controller", "service", "repository", "model", "all"],
            default="all"
        )
        
        # Ejecutar generación
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Generando pruebas...", total=None)
            
            try:
                # Usar agente generador
                result = generation_agent.process_task(
                    type('Task', (), {
                        'task_id': f"generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'description': f"Generar pruebas para {generation_type} en {self.current_project_path}",
                        'priority': 1,
                        'status': 'pending'
                    })()
                )
                
                progress.update(task, description="✅ Generación completada")
                
                # Mostrar resultados
                self._display_generation_results(result)
                
            except Exception as e:
                progress.update(task, description="❌ Error en generación")
                self.console.print(f"[red]Error durante la generación: {e}[/red]")
    
    def _handle_code_validation(self):
        """Manejar validación de código"""
        self.console.print(Panel.fit("Validación de Código", title="✅ Validación"))
        
        if not self.current_project_path:
            self.console.print("[red]Primero debes analizar un proyecto[/red]")
            return
        
        # Ejecutar validación
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Validando código...", total=None)
            
            try:
                # Usar agente validador
                result = validation_agent.process_task(
                    type('Task', (), {
                        'task_id': f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'description': f"Validar código en {self.current_project_path}",
                        'priority': 1,
                        'status': 'pending'
                    })()
                )
                
                progress.update(task, description="✅ Validación completada")
                
                # Mostrar resultados
                self._display_validation_results(result)
                
            except Exception as e:
                progress.update(task, description="❌ Error en validación")
                self.console.print(f"[red]Error durante la validación: {e}[/red]")
    
    def _handle_test_optimization(self):
        """Manejar optimización de pruebas"""
        self.console.print(Panel.fit("Optimización de Pruebas", title="🚀 Optimización"))
        
        if not self.current_project_path:
            self.console.print("[red]Primero debes analizar un proyecto[/red]")
            return
        
        # Ejecutar optimización
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Optimizando pruebas...", total=None)
            
            try:
                # Usar agente optimizador
                result = optimization_agent.process_task(
                    type('Task', (), {
                        'task_id': f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'description': f"Optimizar pruebas en {self.current_project_path}",
                        'priority': 1,
                        'status': 'pending'
                    })()
                )
                
                progress.update(task, description="✅ Optimización completada")
                
                # Mostrar resultados
                self._display_optimization_results(result)
                
            except Exception as e:
                progress.update(task, description="❌ Error en optimización")
                self.console.print(f"[red]Error durante la optimización: {e}[/red]")
    
    def _handle_multi_agent_collaboration(self):
        """Manejar colaboración multi-agente"""
        self.console.print(Panel.fit("Colaboración Multi-Agente", title="🤝 Colaboración"))
        
        # Mostrar capacidades de agentes
        capabilities = self.collaboration.get_agent_capabilities()
        self._display_agent_capabilities(capabilities)
        
        # Solicitar tarea de colaboración
        task_description = Prompt.ask("Describe la tarea para la colaboración multi-agente")
        
        if not task_description:
            self.console.print("[red]Debes proporcionar una descripción de la tarea[/red]")
            return
        
        # Ejecutar colaboración
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Ejecutando colaboración multi-agente...", total=None)
            
            try:
                result = self.collaboration.start_collaboration(task_description)
                
                if result["success"]:
                    progress.update(task, description="✅ Colaboración completada")
                    self.current_session_id = result["session_id"]
                    
                    # Mostrar resultados
                    self._display_collaboration_results(result)
                else:
                    progress.update(task, description="❌ Error en colaboración")
                    self.console.print(f"[red]Error en colaboración: {result.get('error', 'Error desconocido')}[/red]")
                
            except Exception as e:
                progress.update(task, description="❌ Error en colaboración")
                self.console.print(f"[red]Error durante la colaboración: {e}[/red]")
    
    def _handle_memory_management(self):
        """Manejar gestión de memoria"""
        self.console.print(Panel.fit("Gestión de Memoria", title="🧠 Memoria"))
        
        # Mostrar estadísticas de memoria
        memory_stats = self.shared_memory.get_memory_stats()
        self._display_memory_stats(memory_stats)
        
        # Opciones de gestión
        options = [
            "1. Ver entradas de memoria",
            "2. Buscar en memoria",
            "3. Limpiar memoria",
            "4. Exportar memoria",
            "5. Volver al menú principal"
        ]
        
        for option in options:
            self.console.print(f"  {option}")
        
        choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            self._display_memory_entries()
        elif choice == "2":
            self._search_memory()
        elif choice == "3":
            self._clear_memory()
        elif choice == "4":
            self._export_memory()
    
    def _handle_configuration(self):
        """Manejar configuración"""
        self.console.print(Panel.fit("Configuración del Sistema", title="⚙️ Configuración"))
        
        # Mostrar configuración actual
        self._display_current_config()
        
        # Opciones de configuración
        options = [
            "1. Cambiar nivel de logging",
            "2. Configurar API de OpenAI",
            "3. Configurar memoria",
            "4. Configurar agentes",
            "5. Volver al menú principal"
        ]
        
        for option in options:
            self.console.print(f"  {option}")
        
        choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            self._configure_logging()
        elif choice == "2":
            self._configure_openai()
        elif choice == "3":
            self._configure_memory()
        elif choice == "4":
            self._configure_agents()
    
    def _display_analysis_results(self, result: Any):
        """Mostrar resultados de análisis"""
        self.console.print(Panel.fit("Resultados del Análisis", title="📊 Resultados"))
        
        if hasattr(result, 'content'):
            self.console.print(result.content)
        else:
            self.console.print(str(result))
    
    def _display_generation_results(self, result: Any):
        """Mostrar resultados de generación"""
        self.console.print(Panel.fit("Resultados de la Generación", title="⚡ Resultados"))
        
        if hasattr(result, 'content'):
            self.console.print(result.content)
        else:
            self.console.print(str(result))
    
    def _display_validation_results(self, result: Any):
        """Mostrar resultados de validación"""
        self.console.print(Panel.fit("Resultados de la Validación", title="✅ Resultados"))
        
        if hasattr(result, 'content'):
            self.console.print(result.content)
        else:
            self.console.print(str(result))
    
    def _display_optimization_results(self, result: Any):
        """Mostrar resultados de optimización"""
        self.console.print(Panel.fit("Resultados de la Optimización", title="🚀 Resultados"))
        
        if hasattr(result, 'content'):
            self.console.print(result.content)
        else:
            self.console.print(str(result))
    
    def _display_collaboration_results(self, result: Dict[str, Any]):
        """Mostrar resultados de colaboración"""
        self.console.print(Panel.fit("Resultados de la Colaboración", title="🤝 Resultados"))
        
        # Mostrar mensajes del chat grupal
        if "messages" in result:
            for message in result["messages"]:
                self.console.print(f"[bold]{message.get('name', 'Unknown')}:[/bold] {message.get('content', '')}")
        
        # Mostrar resultado final
        if "result" in result:
            self.console.print(f"\n[bold]Resultado Final:[/bold]")
            self.console.print(str(result["result"]))
    
    def _display_agent_capabilities(self, capabilities: Dict[str, List[str]]):
        """Mostrar capacidades de agentes"""
        tree = Tree("🤖 Agentes Disponibles")
        
        for agent_name, agent_capabilities in capabilities.items():
            agent_branch = tree.add(f"[bold]{agent_name}[/bold]")
            for capability in agent_capabilities:
                agent_branch.add(f"• {capability}")
        
        self.console.print(tree)
        self.console.print()
    
    def _display_memory_stats(self, stats: Dict[str, Any]):
        """Mostrar estadísticas de memoria"""
        stats_table = Table(title="Estadísticas de Memoria")
        stats_table.add_column("Métrica", style="cyan")
        stats_table.add_column("Valor", style="green")
        
        for key, value in stats.items():
            stats_table.add_row(key.replace("_", " ").title(), str(value))
        
        self.console.print(stats_table)
        self.console.print()
    
    def _display_memory_entries(self):
        """Mostrar entradas de memoria"""
        # Implementación básica
        self.console.print("Funcionalidad de visualización de entradas de memoria en desarrollo")
    
    def _search_memory(self):
        """Buscar en memoria"""
        query = Prompt.ask("Término de búsqueda")
        if query:
            results = self.shared_memory.search_entries(query)
            self.console.print(f"Encontradas {len(results)} entradas")
    
    def _clear_memory(self):
        """Limpiar memoria"""
        if Confirm.ask("¿Estás seguro de que quieres limpiar toda la memoria?"):
            self.shared_memory.clear_memory()
            self.console.print("[green]Memoria limpiada[/green]")
    
    def _export_memory(self):
        """Exportar memoria"""
        # Implementación básica
        self.console.print("Funcionalidad de exportación de memoria en desarrollo")
    
    def _display_current_config(self):
        """Mostrar configuración actual"""
        config_table = Table(title="Configuración Actual")
        config_table.add_column("Parámetro", style="cyan")
        config_table.add_column("Valor", style="green")
        
        config_table.add_row("Modelo de IA", self.config.ai.model)
        config_table.add_row("Temperatura", str(self.config.ai.temperature))
        config_table.add_row("Nivel de Logging", self.config.agent.log_level)
        config_table.add_row("Modo Multi-Agente", self.config.multi_agent.mode)
        
        self.console.print(config_table)
        self.console.print()
    
    def _configure_logging(self):
        """Configurar logging"""
        level = Prompt.ask("Nivel de logging", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
        self.config.agent.log_level = level
        setup_logging(level=level)
        self.console.print(f"[green]Nivel de logging cambiado a {level}[/green]")
    
    def _configure_openai(self):
        """Configurar OpenAI"""
        api_key = Prompt.ask("API Key de OpenAI", default=self.config.ai.openai_api_key or "")
        if api_key:
            self.config.ai.openai_api_key = api_key
            self.console.print("[green]API Key de OpenAI configurada[/green]")
    
    def _configure_memory(self):
        """Configurar memoria"""
        # Implementación básica
        self.console.print("Configuración de memoria en desarrollo")
    
    def _configure_agents(self):
        """Configurar agentes"""
        # Implementación básica
        self.console.print("Configuración de agentes en desarrollo")
    
    def _shutdown(self):
        """Apagar sistema"""
        self.console.print("Apagando sistema...")
        
        if self.collaboration:
            self.collaboration.shutdown()
        
        self.console.print("[green]Sistema apagado correctamente[/green]")


@click.command()
@click.option('--project-path', '-p', help='Ruta del proyecto .NET a analizar')
@click.option('--config-file', '-c', help='Archivo de configuración personalizado')
@click.option('--log-level', '-l', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']), 
              default='INFO', help='Nivel de logging')
def main(project_path: Optional[str], config_file: Optional[str], log_level: str):
    """IA Agent para Generación de Pruebas Unitarias .NET - Sistema Multi-Agente"""
    
    # Crear instancia del CLI
    cli = MultiAgentCLI()
    
    # Configurar logging
    setup_logging(level=log_level)
    
    # Configurar proyecto si se proporciona
    if project_path:
        cli.current_project_path = project_path
    
    # Inicializar sistema
    if not cli.initialize():
        console.print("[red]Error al inicializar el sistema[/red]")
        sys.exit(1)
    
    # Mostrar menú principal
    try:
        cli.show_main_menu()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrumpido por el usuario[/yellow]")
        cli._shutdown()
    except Exception as e:
        console.print(f"[red]Error inesperado: {e}[/red]")
        cli._shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
