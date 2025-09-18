#!/usr/bin/env python3
"""
Manejador de errores mejorado
IA Agent para Generación de Pruebas Unitarias .NET
"""

import traceback
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import json

from config.environment import environment_manager


class ErrorSeverity(Enum):
    """Severidad del error"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categoría del error"""
    SYSTEM = "system"
    AI = "ai"
    NETWORK = "network"
    FILE = "file"
    MEMORY = "memory"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Información del error"""
    error_id: str
    timestamp: float
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: str
    traceback: str
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution: Optional[str] = None


class ErrorHandler:
    """Manejador centralizado de errores"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = environment_manager.get_config()
        
        # Almacenamiento de errores
        self.errors: List[ErrorInfo] = []
        self.error_counts: Dict[str, int] = {}
        
        # Callbacks de manejo de errores
        self.error_callbacks: Dict[ErrorCategory, List[Callable]] = {
            category: [] for category in ErrorCategory
        }
        
        # Configuración de manejo
        self.max_errors = 1000
        self.auto_retry_enabled = True
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Estadísticas
        self.stats = {
            "total_errors": 0,
            "errors_by_category": {category.value: 0 for category in ErrorCategory},
            "errors_by_severity": {severity.value: 0 for severity in ErrorSeverity},
            "resolved_errors": 0,
            "last_error_time": 0
        }
    
    def handle_error(self, 
                    exception: Exception, 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    category: ErrorCategory = ErrorCategory.UNKNOWN,
                    context: Optional[Dict[str, Any]] = None,
                    auto_retry: bool = False) -> str:
        """Manejar error y devolver ID del error"""
        
        error_id = f"ERR_{int(time.time() * 1000)}"
        timestamp = time.time()
        
        # Crear información del error
        error_info = ErrorInfo(
            error_id=error_id,
            timestamp=timestamp,
            severity=severity,
            category=category,
            message=str(exception),
            exception_type=type(exception).__name__,
            traceback=traceback.format_exc(),
            context=context or {}
        )
        
        # Agregar a la lista de errores
        self.errors.append(error_info)
        
        # Actualizar estadísticas
        self._update_stats(error_info)
        
        # Log del error
        self._log_error(error_info)
        
        # Ejecutar callbacks específicos de la categoría
        self._execute_callbacks(error_info)
        
        # Auto-retry si está habilitado
        if auto_retry and self.auto_retry_enabled:
            return self._handle_auto_retry(error_info)
        
        # Limpiar errores antiguos si es necesario
        self._cleanup_old_errors()
        
        return error_id
    
    def _update_stats(self, error_info: ErrorInfo):
        """Actualizar estadísticas de errores"""
        self.stats["total_errors"] += 1
        self.stats["errors_by_category"][error_info.category.value] += 1
        self.stats["errors_by_severity"][error_info.severity.value] += 1
        self.stats["last_error_time"] = error_info.timestamp
        
        # Contar errores por tipo
        error_key = f"{error_info.category.value}_{error_info.exception_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def _log_error(self, error_info: ErrorInfo):
        """Log del error según su severidad"""
        log_message = f"[{error_info.error_id}] {error_info.message}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, exc_info=True)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, exc_info=True)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _execute_callbacks(self, error_info: ErrorInfo):
        """Ejecutar callbacks de manejo de errores"""
        callbacks = self.error_callbacks.get(error_info.category, [])
        
        for callback in callbacks:
            try:
                callback(error_info)
            except Exception as e:
                self.logger.error(f"Error en callback de manejo de errores: {e}")
    
    def _handle_auto_retry(self, error_info: ErrorInfo) -> str:
        """Manejar reintento automático"""
        # Implementar lógica de reintento según la categoría
        if error_info.category == ErrorCategory.NETWORK:
            return self._retry_network_error(error_info)
        elif error_info.category == ErrorCategory.AI:
            return self._retry_ai_error(error_info)
        
        return error_info.error_id
    
    def _retry_network_error(self, error_info: ErrorInfo) -> str:
        """Reintentar error de red"""
        # Implementar lógica específica para errores de red
        return error_info.error_id
    
    def _retry_ai_error(self, error_info: ErrorInfo) -> str:
        """Reintentar error de IA"""
        # Implementar lógica específica para errores de IA
        return error_info.error_id
    
    def _cleanup_old_errors(self):
        """Limpiar errores antiguos"""
        if len(self.errors) > self.max_errors:
            # Mantener solo los errores más recientes
            self.errors = self.errors[-self.max_errors:]
    
    def add_error_callback(self, category: ErrorCategory, callback: Callable):
        """Agregar callback de manejo de errores"""
        self.error_callbacks[category].append(callback)
        self.logger.info(f"Callback de error agregado para categoría: {category.value}")
    
    def remove_error_callback(self, category: ErrorCategory, callback: Callable):
        """Remover callback de manejo de errores"""
        if callback in self.error_callbacks[category]:
            self.error_callbacks[category].remove(callback)
            self.logger.info(f"Callback de error removido para categoría: {category.value}")
    
    def resolve_error(self, error_id: str, resolution: str):
        """Marcar error como resuelto"""
        for error in self.errors:
            if error.error_id == error_id:
                error.resolved = True
                error.resolution = resolution
                self.stats["resolved_errors"] += 1
                self.logger.info(f"Error resuelto: {error_id}")
                break
    
    def get_error(self, error_id: str) -> Optional[ErrorInfo]:
        """Obtener información de un error específico"""
        for error in self.errors:
            if error.error_id == error_id:
                return error
        return None
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorInfo]:
        """Obtener errores por categoría"""
        return [error for error in self.errors if error.category == category]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorInfo]:
        """Obtener errores por severidad"""
        return [error for error in self.errors if error.severity == severity]
    
    def get_unresolved_errors(self) -> List[ErrorInfo]:
        """Obtener errores no resueltos"""
        return [error for error in self.errors if not error.resolved]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de errores"""
        return {
            "stats": self.stats.copy(),
            "error_counts": self.error_counts.copy(),
            "total_errors_stored": len(self.errors),
            "unresolved_errors": len(self.get_unresolved_errors()),
            "callbacks_registered": {
                category.value: len(callbacks) 
                for category, callbacks in self.error_callbacks.items()
            }
        }
    
    def clear_errors(self):
        """Limpiar todos los errores"""
        self.errors.clear()
        self.error_counts.clear()
        self.stats = {
            "total_errors": 0,
            "errors_by_category": {category.value: 0 for category in ErrorCategory},
            "errors_by_severity": {severity.value: 0 for severity in ErrorSeverity},
            "resolved_errors": 0,
            "last_error_time": 0
        }
        self.logger.info("Todos los errores han sido limpiados")


def error_handler_decorator(severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                           category: ErrorCategory = ErrorCategory.UNKNOWN,
                           auto_retry: bool = False):
    """Decorador para manejo automático de errores"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(
                    exception=e,
                    severity=severity,
                    category=category,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],  # Limitar tamaño
                        "kwargs": str(kwargs)[:200]
                    },
                    auto_retry=auto_retry
                )
                raise  # Re-lanzar la excepción
        return wrapper
    return decorator


# Instancia global del manejador de errores
error_handler = ErrorHandler()
