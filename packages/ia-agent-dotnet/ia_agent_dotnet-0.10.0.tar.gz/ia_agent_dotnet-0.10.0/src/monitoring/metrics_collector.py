"""
Recolector de métricas del sistema
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import threading
from pathlib import Path

from utils.logging import get_logger

logger = get_logger("metrics-collector")


@dataclass
class Metric:
    """Métrica individual"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_sessions: int
    requests_per_minute: float
    average_response_time: float
    error_rate: float


class MetricsCollector:
    """Recolector de métricas del sistema"""
    
    def __init__(self, storage_path: str = "./metrics"):
        self.logger = logger
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.metrics: List[Metric] = []
        self.system_metrics: List[SystemMetrics] = []
        self.lock = threading.Lock()
        
        # Configuración
        self.max_metrics = 10000
        self.retention_days = 30
        
        self.logger.info("Recolector de métricas inicializado")
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Registrar una métrica"""
        try:
            with self.lock:
                metric = Metric(
                    name=name,
                    value=value,
                    timestamp=datetime.now(),
                    tags=tags or {},
                    metadata=metadata or {}
                )
                
                self.metrics.append(metric)
                
                # Limpiar métricas antiguas si es necesario
                if len(self.metrics) > self.max_metrics:
                    self.metrics = self.metrics[-self.max_metrics:]
                
                self.logger.debug(f"Métrica registrada: {name} = {value}")
                
        except Exception as e:
            self.logger.error(f"Error al registrar métrica: {e}")
    
    def record_system_metrics(self, metrics: SystemMetrics):
        """Registrar métricas del sistema"""
        try:
            with self.lock:
                self.system_metrics.append(metrics)
                
                # Limpiar métricas antiguas
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                self.system_metrics = [m for m in self.system_metrics if m.timestamp > cutoff_date]
                
                self.logger.debug("Métricas del sistema registradas")
                
        except Exception as e:
            self.logger.error(f"Error al registrar métricas del sistema: {e}")
    
    def get_metrics(self, name: Optional[str] = None, tags: Optional[Dict[str, str]] = None, 
                   start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Metric]:
        """Obtener métricas filtradas"""
        try:
            with self.lock:
                filtered_metrics = self.metrics.copy()
                
                # Filtrar por nombre
                if name:
                    filtered_metrics = [m for m in filtered_metrics if m.name == name]
                
                # Filtrar por tags
                if tags:
                    filtered_metrics = [m for m in filtered_metrics 
                                      if all(m.tags.get(k) == v for k, v in tags.items())]
                
                # Filtrar por tiempo
                if start_time:
                    filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
                
                if end_time:
                    filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
                
                return filtered_metrics
                
        except Exception as e:
            self.logger.error(f"Error al obtener métricas: {e}")
            return []
    
    def get_system_metrics(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[SystemMetrics]:
        """Obtener métricas del sistema"""
        try:
            with self.lock:
                filtered_metrics = self.system_metrics.copy()
                
                if start_time:
                    filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
                
                if end_time:
                    filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
                
                return filtered_metrics
                
        except Exception as e:
            self.logger.error(f"Error al obtener métricas del sistema: {e}")
            return []
    
    def get_metric_summary(self, name: str, period_hours: int = 24) -> Dict[str, Any]:
        """Obtener resumen de una métrica"""
        try:
            start_time = datetime.now() - timedelta(hours=period_hours)
            metrics = self.get_metrics(name=name, start_time=start_time)
            
            if not metrics:
                return {"error": "No hay métricas disponibles"}
            
            values = [m.value for m in metrics]
            
            return {
                "name": name,
                "period_hours": period_hours,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1] if values else None,
                "trend": self._calculate_trend(values)
            }
            
        except Exception as e:
            self.logger.error(f"Error al obtener resumen de métrica: {e}")
            return {"error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcular tendencia de valores"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Comparar primera mitad con segunda mitad
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid
        second_half_avg = sum(values[mid:]) / (len(values) - mid)
        
        if second_half_avg > first_half_avg * 1.05:
            return "increasing"
        elif second_half_avg < first_half_avg * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def save_metrics(self, file_path: Optional[str] = None):
        """Guardar métricas en archivo"""
        try:
            if not file_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = self.storage_path / f"metrics_{timestamp}.json"
            
            with self.lock:
                data = {
                    "metrics": [
                        {
                            "name": m.name,
                            "value": m.value,
                            "timestamp": m.timestamp.isoformat(),
                            "tags": m.tags,
                            "metadata": m.metadata
                        }
                        for m in self.metrics
                    ],
                    "system_metrics": [
                        {
                            "timestamp": m.timestamp.isoformat(),
                            "cpu_usage": m.cpu_usage,
                            "memory_usage": m.memory_usage,
                            "disk_usage": m.disk_usage,
                            "active_sessions": m.active_sessions,
                            "requests_per_minute": m.requests_per_minute,
                            "average_response_time": m.average_response_time,
                            "error_rate": m.error_rate
                        }
                        for m in self.system_metrics
                    ]
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Métricas guardadas en: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error al guardar métricas: {e}")
    
    def load_metrics(self, file_path: str):
        """Cargar métricas desde archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with self.lock:
                # Cargar métricas
                self.metrics = []
                for m_data in data.get("metrics", []):
                    metric = Metric(
                        name=m_data["name"],
                        value=m_data["value"],
                        timestamp=datetime.fromisoformat(m_data["timestamp"]),
                        tags=m_data.get("tags", {}),
                        metadata=m_data.get("metadata", {})
                    )
                    self.metrics.append(metric)
                
                # Cargar métricas del sistema
                self.system_metrics = []
                for sm_data in data.get("system_metrics", []):
                    system_metric = SystemMetrics(
                        timestamp=datetime.fromisoformat(sm_data["timestamp"]),
                        cpu_usage=sm_data["cpu_usage"],
                        memory_usage=sm_data["memory_usage"],
                        disk_usage=sm_data["disk_usage"],
                        active_sessions=sm_data["active_sessions"],
                        requests_per_minute=sm_data["requests_per_minute"],
                        average_response_time=sm_data["average_response_time"],
                        error_rate=sm_data["error_rate"]
                    )
                    self.system_metrics.append(system_metric)
            
            self.logger.info(f"Métricas cargadas desde: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error al cargar métricas: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtener datos para dashboard"""
        try:
            # Métricas de las últimas 24 horas
            start_time = datetime.now() - timedelta(hours=24)
            
            # Métricas principales
            response_times = self.get_metrics("response_time", start_time=start_time)
            error_counts = self.get_metrics("error_count", start_time=start_time)
            success_counts = self.get_metrics("success_count", start_time=start_time)
            
            # Métricas del sistema
            system_metrics = self.get_system_metrics(start_time=start_time)
            
            return {
                "performance": {
                    "avg_response_time": sum(m.value for m in response_times) / len(response_times) if response_times else 0,
                    "total_requests": len(response_times),
                    "error_rate": len(error_counts) / (len(error_counts) + len(success_counts)) if (error_counts or success_counts) else 0
                },
                "system": {
                    "avg_cpu": sum(m.cpu_usage for m in system_metrics) / len(system_metrics) if system_metrics else 0,
                    "avg_memory": sum(m.memory_usage for m in system_metrics) / len(system_metrics) if system_metrics else 0,
                    "active_sessions": system_metrics[-1].active_sessions if system_metrics else 0
                },
                "trends": {
                    "response_time_trend": self._calculate_trend([m.value for m in response_times]),
                    "error_rate_trend": self._calculate_trend([m.value for m in error_counts])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error al obtener datos del dashboard: {e}")
            return {"error": str(e)}
