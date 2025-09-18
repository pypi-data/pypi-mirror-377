"""
Sistema de logging para el agente
IA Agent para Generación de Pruebas Unitarias .NET
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler


class AgentLogger:
    """Logger personalizado para el agente"""
    
    def __init__(self, name: str = "ia-agent", level: str = "INFO"):
        self.name = name
        self.level = level
        self.console = Console()
        self._setup_logger()
    
    def _setup_logger(self):
        """Configurar el logger"""
        # Remover handlers por defecto
        logger.remove()
        
        # Configurar formato
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Handler para consola con Rich
        logger.add(
            sys.stdout,
            format=format_string,
            level=self.level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # Handler para archivo
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logger.add(
            log_dir / "agent.log",
            format=format_string,
            level=self.level,
            rotation="10 MB",
            retention="5 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Handler para errores
        logger.add(
            log_dir / "errors.log",
            format=format_string,
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
    
    def get_logger(self, component: Optional[str] = None) -> logger:
        """Obtener logger para un componente específico"""
        if component:
            return logger.bind(component=component)
        return logger
    
    def set_level(self, level: str):
        """Cambiar nivel de logging"""
        self.level = level
        self._setup_logger()


class ComponentLogger:
    """Logger para componentes específicos del agente"""
    
    def __init__(self, component_name: str, parent_logger: Optional[AgentLogger] = None):
        self.component_name = component_name
        self.logger = (parent_logger or AgentLogger()).get_logger(component_name)
    
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        self.logger.debug(f"[{self.component_name}] {message}", **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log de información"""
        self.logger.info(f"[{self.component_name}] {message}", **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de advertencia"""
        self.logger.warning(f"[{self.component_name}] {message}", **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de error"""
        self.logger.error(f"[{self.component_name}] {message}", **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico"""
        self.logger.critical(f"[{self.component_name}] {message}", **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log de éxito"""
        self.logger.success(f"[{self.component_name}] {message}", **kwargs)


# Instancia global del logger principal
main_logger = AgentLogger()


def get_logger(component: Optional[str] = None) -> ComponentLogger:
    """Obtener logger para un componente específico"""
    return ComponentLogger(component or "main", main_logger)


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Configurar logging del sistema"""
    global main_logger
    main_logger = AgentLogger(level=level)
    
    if log_file:
        # Agregar handler adicional para archivo específico
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=level,
            rotation="10 MB",
            retention="5 days"
        )


# Loggers específicos para componentes principales
agent_logger = get_logger("agent")
memory_logger = get_logger("memory")
tools_logger = get_logger("tools")
generation_logger = get_logger("generation")
multi_agent_logger = get_logger("multi-agent")
