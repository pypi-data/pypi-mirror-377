"""
Dashboard para visualización de métricas
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from utils.logging import get_logger

logger = get_logger("dashboard")


@dataclass
class DashboardData:
    """Datos del dashboard"""
    timestamp: datetime
    system_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    agent_metrics: Dict[str, Any]
    alerts: List[str]


class Dashboard:
    """Dashboard para visualización de métricas"""
    
    def __init__(self):
        self.logger = logger
        self.data_history: List[DashboardData] = []
        self.max_history = 1000
    
    def generate_dashboard_data(self, 
                              system_metrics: Optional[Dict[str, Any]] = None,
                              performance_metrics: Optional[Dict[str, Any]] = None,
                              quality_metrics: Optional[Dict[str, Any]] = None,
                              agent_metrics: Optional[Dict[str, Any]] = None) -> DashboardData:
        """Generar datos del dashboard"""
        try:
            # Datos por defecto si no se proporcionan
            if system_metrics is None:
                system_metrics = self._get_default_system_metrics()
            
            if performance_metrics is None:
                performance_metrics = self._get_default_performance_metrics()
            
            if quality_metrics is None:
                quality_metrics = self._get_default_quality_metrics()
            
            if agent_metrics is None:
                agent_metrics = self._get_default_agent_metrics()
            
            # Generar alertas
            alerts = self._generate_alerts(system_metrics, performance_metrics, quality_metrics)
            
            # Crear datos del dashboard
            dashboard_data = DashboardData(
                timestamp=datetime.now(),
                system_metrics=system_metrics,
                performance_metrics=performance_metrics,
                quality_metrics=quality_metrics,
                agent_metrics=agent_metrics,
                alerts=alerts
            )
            
            # Agregar al historial
            self.data_history.append(dashboard_data)
            
            # Limpiar historial si es necesario
            if len(self.data_history) > self.max_history:
                self.data_history = self.data_history[-self.max_history:]
            
            self.logger.info("Datos del dashboard generados")
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error al generar datos del dashboard: {e}")
            return self._get_default_dashboard_data()
    
    def _get_default_system_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema por defecto"""
        return {
            "status": "unknown",
            "uptime": "0h 0m",
            "version": "1.0.0",
            "environment": "development",
            "last_update": datetime.now().isoformat()
        }
    
    def _get_default_performance_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento por defecto"""
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "response_time": 0.0,
            "throughput": 0.0,
            "error_rate": 0.0
        }
    
    def _get_default_quality_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de calidad por defecto"""
        return {
            "overall_score": 0.0,
            "complexity_score": 0.0,
            "maintainability_score": 0.0,
            "readability_score": 0.0,
            "test_coverage": 0.0,
            "issues_count": 0
        }
    
    def _get_default_agent_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de agentes por defecto"""
        return {
            "total_agents": 0,
            "active_agents": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }
    
    def _get_default_dashboard_data(self) -> DashboardData:
        """Obtener datos del dashboard por defecto"""
        return DashboardData(
            timestamp=datetime.now(),
            system_metrics=self._get_default_system_metrics(),
            performance_metrics=self._get_default_performance_metrics(),
            quality_metrics=self._get_default_quality_metrics(),
            agent_metrics=self._get_default_agent_metrics(),
            alerts=["Error al generar datos del dashboard"]
        )
    
    def _generate_alerts(self, 
                        system_metrics: Dict[str, Any],
                        performance_metrics: Dict[str, Any],
                        quality_metrics: Dict[str, Any]) -> List[str]:
        """Generar alertas basadas en métricas"""
        alerts = []
        
        # Alertas de rendimiento
        if performance_metrics.get("cpu_usage", 0) > 80:
            alerts.append("CPU usage is high (>80%)")
        
        if performance_metrics.get("memory_usage", 0) > 80:
            alerts.append("Memory usage is high (>80%)")
        
        if performance_metrics.get("disk_usage", 0) > 90:
            alerts.append("Disk space is low (>90%)")
        
        if performance_metrics.get("error_rate", 0) > 5:
            alerts.append("Error rate is high (>5%)")
        
        # Alertas de calidad
        if quality_metrics.get("overall_score", 0) < 0.5:
            alerts.append("Code quality is below acceptable threshold")
        
        if quality_metrics.get("test_coverage", 0) < 0.7:
            alerts.append("Test coverage is below recommended level (70%)")
        
        if quality_metrics.get("issues_count", 0) > 10:
            alerts.append("High number of code quality issues detected")
        
        # Alertas del sistema
        if system_metrics.get("status") != "healthy":
            alerts.append("System status is not healthy")
        
        if not alerts:
            alerts.append("All systems operating normally")
        
        return alerts
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Obtener resumen del dashboard"""
        if not self.data_history:
            return {"message": "No hay datos disponibles"}
        
        latest_data = self.data_history[-1]
        
        return {
            "timestamp": latest_data.timestamp.isoformat(),
            "status": self._get_overall_status(latest_data),
            "alerts_count": len(latest_data.alerts),
            "critical_alerts": [alert for alert in latest_data.alerts if "critical" in alert.lower()],
            "system_health": self._calculate_system_health(latest_data),
            "trends": self._calculate_trends()
        }
    
    def _get_overall_status(self, data: DashboardData) -> str:
        """Obtener estado general del sistema"""
        critical_alerts = [alert for alert in data.alerts if "critical" in alert.lower()]
        
        if critical_alerts:
            return "critical"
        elif len(data.alerts) > 3:
            return "warning"
        else:
            return "healthy"
    
    def _calculate_system_health(self, data: DashboardData) -> float:
        """Calcular salud del sistema (0-1)"""
        health_score = 1.0
        
        # Penalizar por alertas
        health_score -= len(data.alerts) * 0.1
        
        # Penalizar por métricas de rendimiento
        if data.performance_metrics.get("cpu_usage", 0) > 80:
            health_score -= 0.2
        
        if data.performance_metrics.get("memory_usage", 0) > 80:
            health_score -= 0.2
        
        if data.performance_metrics.get("error_rate", 0) > 5:
            health_score -= 0.3
        
        # Penalizar por calidad
        if data.quality_metrics.get("overall_score", 0) < 0.5:
            health_score -= 0.2
        
        return max(0.0, health_score)
    
    def _calculate_trends(self) -> Dict[str, str]:
        """Calcular tendencias"""
        if len(self.data_history) < 2:
            return {"trend": "insufficient_data"}
        
        # Comparar últimos 2 puntos de datos
        current = self.data_history[-1]
        previous = self.data_history[-2]
        
        trends = {}
        
        # Tendencia de CPU
        current_cpu = current.performance_metrics.get("cpu_usage", 0)
        previous_cpu = previous.performance_metrics.get("cpu_usage", 0)
        
        if current_cpu > previous_cpu * 1.05:
            trends["cpu"] = "increasing"
        elif current_cpu < previous_cpu * 0.95:
            trends["cpu"] = "decreasing"
        else:
            trends["cpu"] = "stable"
        
        # Tendencia de memoria
        current_memory = current.performance_metrics.get("memory_usage", 0)
        previous_memory = previous.performance_metrics.get("memory_usage", 0)
        
        if current_memory > previous_memory * 1.05:
            trends["memory"] = "increasing"
        elif current_memory < previous_memory * 0.95:
            trends["memory"] = "decreasing"
        else:
            trends["memory"] = "stable"
        
        # Tendencia de calidad
        current_quality = current.quality_metrics.get("overall_score", 0)
        previous_quality = previous.quality_metrics.get("overall_score", 0)
        
        if current_quality > previous_quality * 1.05:
            trends["quality"] = "improving"
        elif current_quality < previous_quality * 0.95:
            trends["quality"] = "degrading"
        else:
            trends["quality"] = "stable"
        
        return trends
    
    def export_dashboard_data(self, format: str = "json") -> str:
        """Exportar datos del dashboard"""
        try:
            if format.lower() == "json":
                data = {
                    "dashboard_data": [
                        {
                            "timestamp": d.timestamp.isoformat(),
                            "system_metrics": d.system_metrics,
                            "performance_metrics": d.performance_metrics,
                            "quality_metrics": d.quality_metrics,
                            "agent_metrics": d.agent_metrics,
                            "alerts": d.alerts
                        }
                        for d in self.data_history
                    ],
                    "summary": self.get_dashboard_summary()
                }
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Formato no soportado: {format}")
                
        except Exception as e:
            self.logger.error(f"Error al exportar datos del dashboard: {e}")
            return json.dumps({"error": str(e)})
    
    def get_historical_data(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtener datos históricos"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        historical_data = [
            {
                "timestamp": d.timestamp.isoformat(),
                "system_metrics": d.system_metrics,
                "performance_metrics": d.performance_metrics,
                "quality_metrics": d.quality_metrics,
                "agent_metrics": d.agent_metrics,
                "alerts": d.alerts
            }
            for d in self.data_history
            if d.timestamp >= cutoff_time
        ]
        
        return historical_data
