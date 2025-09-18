"""
Monitor de rendimiento del sistema
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import psutil
import time
import threading

from utils.logging import get_logger

logger = get_logger("performance-monitor")


@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    active_threads: int
    python_memory_mb: float


class PerformanceMonitor:
    """Monitor de rendimiento del sistema"""
    
    def __init__(self, monitoring_interval: int = 60):
        self.logger = logger
        self.monitoring_interval = monitoring_interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
    
    def start_monitoring(self):
        """Iniciar monitoreo en segundo plano"""
        if self.is_monitoring:
            self.logger.warning("El monitoreo ya está activo")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Monitoreo de rendimiento iniciado")
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Monitoreo de rendimiento detenido")
    
    def _monitor_loop(self):
        """Loop de monitoreo"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                with self.lock:
                    self.metrics_history.append(metrics)
                    
                    # Mantener solo las últimas 1000 métricas
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error en loop de monitoreo: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Recopilar métricas del sistema"""
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
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            
            # Threads
            active_threads = threading.active_count()
            
            # Memoria de Python
            process = psutil.Process()
            python_memory_mb = process.memory_info().rss / (1024 * 1024)
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                active_threads=active_threads,
                python_memory_mb=python_memory_mb
            )
            
        except Exception as e:
            self.logger.error(f"Error al recopilar métricas: {e}")
            # Retornar métricas por defecto
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                active_threads=0,
                python_memory_mb=0.0
            )
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Obtener métricas actuales"""
        return self._collect_metrics()
    
    def get_metrics_history(self, hours: int = 24) -> List[PerformanceMetrics]:
        """Obtener historial de métricas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_average_metrics(self, hours: int = 1) -> Dict[str, float]:
        """Obtener métricas promedio"""
        metrics = self.get_metrics_history(hours)
        
        if not metrics:
            return {}
        
        return {
            "avg_cpu_percent": sum(m.cpu_percent for m in metrics) / len(metrics),
            "avg_memory_percent": sum(m.memory_percent for m in metrics) / len(metrics),
            "avg_memory_used_mb": sum(m.memory_used_mb for m in metrics) / len(metrics),
            "avg_disk_usage_percent": sum(m.disk_usage_percent for m in metrics) / len(metrics),
            "avg_active_threads": sum(m.active_threads for m in metrics) / len(metrics),
            "avg_python_memory_mb": sum(m.python_memory_mb for m in metrics) / len(metrics)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtener resumen de rendimiento"""
        current = self.get_current_metrics()
        averages = self.get_average_metrics(1)
        
        return {
            "current": {
                "cpu_percent": current.cpu_percent,
                "memory_percent": current.memory_percent,
                "memory_used_mb": current.memory_used_mb,
                "disk_usage_percent": current.disk_usage_percent,
                "active_threads": current.active_threads,
                "python_memory_mb": current.python_memory_mb
            },
            "averages_1h": averages,
            "status": self._get_performance_status(current),
            "recommendations": self._get_recommendations(current)
        }
    
    def _get_performance_status(self, metrics: PerformanceMetrics) -> str:
        """Obtener estado de rendimiento"""
        if metrics.cpu_percent > 90 or metrics.memory_percent > 90:
            return "critical"
        elif metrics.cpu_percent > 70 or metrics.memory_percent > 70:
            return "warning"
        elif metrics.cpu_percent > 50 or metrics.memory_percent > 50:
            return "moderate"
        else:
            return "good"
    
    def _get_recommendations(self, metrics: PerformanceMetrics) -> List[str]:
        """Obtener recomendaciones de rendimiento"""
        recommendations = []
        
        if metrics.cpu_percent > 80:
            recommendations.append("CPU usage is high. Consider optimizing CPU-intensive operations.")
        
        if metrics.memory_percent > 80:
            recommendations.append("Memory usage is high. Consider reducing memory consumption.")
        
        if metrics.disk_usage_percent > 90:
            recommendations.append("Disk space is low. Consider cleaning up temporary files.")
        
        if metrics.python_memory_mb > 1000:
            recommendations.append("Python memory usage is high. Consider optimizing memory usage.")
        
        if metrics.active_threads > 100:
            recommendations.append("High number of active threads. Consider thread pool optimization.")
        
        if not recommendations:
            recommendations.append("System performance is within normal parameters.")
        
        return recommendations
