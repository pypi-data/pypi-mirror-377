#!/usr/bin/env python3
"""
Optimizador de rendimiento del sistema
IA Agent para Generación de Pruebas Unitarias .NET
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging

from config.environment import environment_manager


@dataclass
class PerformanceMetric:
    """Métrica de rendimiento"""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    unit: str = "ms"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemResource:
    """Recurso del sistema"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    timestamp: float = field(default_factory=time.time)


class PerformanceOptimizer:
    """Optimizador de rendimiento del sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = environment_manager.get_config()
        
        # Métricas de rendimiento
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.resource_history: deque = deque(maxlen=100)
        
        # Locks para thread safety
        self.metrics_lock = threading.RLock()
        self.resource_lock = threading.RLock()
        
        # Configuración de optimización
        self.optimization_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "response_time_ms": 5000.0,
            "cache_hit_rate": 70.0
        }
        
        # Estado de optimización
        self.optimization_active = False
        self.last_optimization = 0
        self.optimization_interval = 300  # 5 minutos
        
        # Callbacks de optimización
        self.optimization_callbacks: List[Callable] = []
        
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Iniciar monitoreo de recursos"""
        def monitor_resources():
            while True:
                try:
                    resource = self._collect_system_resources()
                    with self.resource_lock:
                        self.resource_history.append(resource)
                    
                    # Verificar si necesita optimización
                    if self._should_optimize(resource):
                        self._trigger_optimization()
                    
                    time.sleep(30)  # Monitorear cada 30 segundos
                    
                except Exception as e:
                    self.logger.error(f"Error en monitoreo de recursos: {e}")
                    time.sleep(60)  # Esperar más tiempo en caso de error
        
        # Iniciar thread de monitoreo
        monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        monitor_thread.start()
        self.logger.info("Monitoreo de rendimiento iniciado")
    
    def _collect_system_resources(self) -> SystemResource:
        """Recopilar recursos del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            return SystemResource(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent
            )
            
        except Exception as e:
            self.logger.error(f"Error al recopilar recursos del sistema: {e}")
            return SystemResource(0, 0, 0, 0, 0)
    
    def _should_optimize(self, resource: SystemResource) -> bool:
        """Verificar si se necesita optimización"""
        current_time = time.time()
        
        # Verificar intervalos
        if current_time - self.last_optimization < self.optimization_interval:
            return False
        
        # Verificar umbrales
        if (resource.cpu_percent > self.optimization_thresholds["cpu_percent"] or
            resource.memory_percent > self.optimization_thresholds["memory_percent"]):
            return True
        
        return False
    
    def _trigger_optimization(self):
        """Activar optimización"""
        if self.optimization_active:
            return
        
        self.optimization_active = True
        self.last_optimization = time.time()
        
        try:
            self.logger.info("Iniciando optimización automática del sistema")
            
            # Ejecutar callbacks de optimización
            for callback in self.optimization_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Error en callback de optimización: {e}")
            
            self.logger.info("Optimización automática completada")
            
        except Exception as e:
            self.logger.error(f"Error en optimización automática: {e}")
        finally:
            self.optimization_active = False
    
    def add_metric(self, name: str, value: float, unit: str = "ms", metadata: Optional[Dict] = None):
        """Agregar métrica de rendimiento"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            metadata=metadata or {}
        )
        
        with self.metrics_lock:
            self.metrics[name].append(metric)
    
    def get_metric_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtener estadísticas de una métrica"""
        with self.metrics_lock:
            if name not in self.metrics or not self.metrics[name]:
                return None
            
            values = [m.value for m in self.metrics[name]]
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1],
                "unit": self.metrics[name][-1].unit
            }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Obtener todas las métricas"""
        with self.metrics_lock:
            return {
                name: self.get_metric_stats(name)
                for name in self.metrics.keys()
            }
    
    def get_system_resources(self) -> Optional[SystemResource]:
        """Obtener recursos actuales del sistema"""
        with self.resource_lock:
            if self.resource_history:
                return self.resource_history[-1]
            return None
    
    def get_resource_history(self, limit: int = 10) -> List[SystemResource]:
        """Obtener historial de recursos"""
        with self.resource_lock:
            return list(self.resource_history)[-limit:]
    
    def add_optimization_callback(self, callback: Callable):
        """Agregar callback de optimización"""
        self.optimization_callbacks.append(callback)
        self.logger.info(f"Callback de optimización agregado: {callback.__name__}")
    
    def remove_optimization_callback(self, callback: Callable):
        """Remover callback de optimización"""
        if callback in self.optimization_callbacks:
            self.optimization_callbacks.remove(callback)
            self.logger.info(f"Callback de optimización removido: {callback.__name__}")
    
    def optimize_now(self) -> Dict[str, Any]:
        """Forzar optimización inmediata"""
        self.logger.info("Optimización manual iniciada")
        
        optimization_results = {
            "timestamp": time.time(),
            "system_resources": self.get_system_resources(),
            "metrics_before": self.get_all_metrics(),
            "optimizations_applied": []
        }
        
        try:
            # Ejecutar callbacks de optimización
            for callback in self.optimization_callbacks:
                try:
                    result = callback()
                    optimization_results["optimizations_applied"].append({
                        "callback": callback.__name__,
                        "result": result
                    })
                except Exception as e:
                    self.logger.error(f"Error en callback de optimización: {e}")
                    optimization_results["optimizations_applied"].append({
                        "callback": callback.__name__,
                        "error": str(e)
                    })
            
            optimization_results["metrics_after"] = self.get_all_metrics()
            optimization_results["success"] = True
            
            self.logger.info("Optimización manual completada")
            
        except Exception as e:
            self.logger.error(f"Error en optimización manual: {e}")
            optimization_results["error"] = str(e)
            optimization_results["success"] = False
        
        return optimization_results
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Obtener reporte de rendimiento"""
        current_resources = self.get_system_resources()
        all_metrics = self.get_all_metrics()
        
        # Calcular métricas agregadas
        total_metrics = sum(len(metrics) for metrics in self.metrics.values())
        active_optimization = self.optimization_active
        
        return {
            "timestamp": time.time(),
            "system_resources": current_resources.__dict__ if current_resources else None,
            "metrics": all_metrics,
            "total_metrics_collected": total_metrics,
            "optimization_active": active_optimization,
            "last_optimization": self.last_optimization,
            "optimization_callbacks": len(self.optimization_callbacks),
            "thresholds": self.optimization_thresholds
        }
    
    def update_thresholds(self, **kwargs):
        """Actualizar umbrales de optimización"""
        for key, value in kwargs.items():
            if key in self.optimization_thresholds:
                old_value = self.optimization_thresholds[key]
                self.optimization_thresholds[key] = value
                self.logger.info(f"Umbral actualizado: {key} {old_value} -> {value}")
    
    def reset_metrics(self):
        """Resetear métricas"""
        with self.metrics_lock:
            self.metrics.clear()
        
        with self.resource_lock:
            self.resource_history.clear()
        
        self.logger.info("Métricas de rendimiento reseteadas")


# Instancia global del optimizador de rendimiento
performance_optimizer = PerformanceOptimizer()
