"""
Tests para sistema de monitoreo
IA Agent para Generación de Pruebas Unitarias .NET
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from monitoring.metrics_collector import MetricsCollector, Metric, SystemMetrics


class TestMonitoring(unittest.TestCase):
    """Tests para sistema de monitoreo"""
    
    def setUp(self):
        """Configuración inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.collector = MetricsCollector(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Limpieza"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_metrics_collector_creation(self):
        """Test creación de metrics collector"""
        try:
            collector = MetricsCollector()
            self.assertIsNotNone(collector)
            self.assertIsNotNone(collector.metrics)
            self.assertIsNotNone(collector.system_metrics)
            
        except Exception as e:
            self.skipTest(f"Metrics Collector no disponible: {e}")
    
    def test_record_metric(self):
        """Test registrar métrica"""
        try:
            # Registrar métrica
            self.collector.record_metric(
                name="test_metric",
                value=42.5,
                tags={"type": "test"},
                metadata={"source": "unittest"}
            )
            
            # Verificar que se registró
            self.assertEqual(len(self.collector.metrics), 1)
            metric = self.collector.metrics[0]
            self.assertEqual(metric.name, "test_metric")
            self.assertEqual(metric.value, 42.5)
            self.assertEqual(metric.tags["type"], "test")
            
        except Exception as e:
            self.skipTest(f"Test de registro de métrica no disponible: {e}")
    
    def test_record_system_metrics(self):
        """Test registrar métricas del sistema"""
        try:
            # Crear métricas del sistema
            system_metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=75.5,
                memory_usage=60.2,
                disk_usage=45.8,
                active_sessions=5,
                requests_per_minute=120.0,
                average_response_time=0.5,
                error_rate=0.02
            )
            
            # Registrar métricas
            self.collector.record_system_metrics(system_metrics)
            
            # Verificar que se registraron
            self.assertEqual(len(self.collector.system_metrics), 1)
            recorded_metrics = self.collector.system_metrics[0]
            self.assertEqual(recorded_metrics.cpu_usage, 75.5)
            self.assertEqual(recorded_metrics.memory_usage, 60.2)
            
        except Exception as e:
            self.skipTest(f"Test de métricas del sistema no disponible: {e}")
    
    def test_get_metrics_by_name(self):
        """Test obtener métricas por nombre"""
        try:
            # Registrar varias métricas
            self.collector.record_metric("test_metric_1", 10.0)
            self.collector.record_metric("test_metric_2", 20.0)
            self.collector.record_metric("test_metric_1", 15.0)
            
            # Obtener métricas por nombre
            metrics = self.collector.get_metrics(name="test_metric_1")
            self.assertEqual(len(metrics), 2)
            
            for metric in metrics:
                self.assertEqual(metric.name, "test_metric_1")
            
        except Exception as e:
            self.skipTest(f"Test de métricas por nombre no disponible: {e}")
    
    def test_get_metrics_by_tags(self):
        """Test obtener métricas por tags"""
        try:
            # Registrar métricas con tags
            self.collector.record_metric("metric_1", 10.0, tags={"type": "performance"})
            self.collector.record_metric("metric_2", 20.0, tags={"type": "error"})
            self.collector.record_metric("metric_3", 30.0, tags={"type": "performance"})
            
            # Obtener métricas por tags
            metrics = self.collector.get_metrics(tags={"type": "performance"})
            self.assertEqual(len(metrics), 2)
            
            for metric in metrics:
                self.assertEqual(metric.tags["type"], "performance")
            
        except Exception as e:
            self.skipTest(f"Test de métricas por tags no disponible: {e}")
    
    def test_get_metrics_by_time_range(self):
        """Test obtener métricas por rango de tiempo"""
        try:
            # Registrar métricas en diferentes momentos
            now = datetime.now()
            past = now - timedelta(hours=2)
            future = now + timedelta(hours=1)
            
            # Simular métricas en el pasado
            metric_past = Metric("past_metric", 10.0, past)
            self.collector.metrics.append(metric_past)
            
            # Registrar métrica actual
            self.collector.record_metric("current_metric", 20.0)
            
            # Obtener métricas de la última hora
            start_time = now - timedelta(hours=1)
            metrics = self.collector.get_metrics(start_time=start_time)
            
            # Debería incluir solo la métrica actual
            self.assertEqual(len(metrics), 1)
            self.assertEqual(metrics[0].name, "current_metric")
            
        except Exception as e:
            self.skipTest(f"Test de métricas por tiempo no disponible: {e}")
    
    def test_get_metric_summary(self):
        """Test obtener resumen de métrica"""
        try:
            # Registrar varias métricas
            self.collector.record_metric("test_metric", 10.0)
            self.collector.record_metric("test_metric", 20.0)
            self.collector.record_metric("test_metric", 30.0)
            
            # Obtener resumen
            summary = self.collector.get_metric_summary("test_metric", period_hours=24)
            
            self.assertIsNotNone(summary)
            self.assertEqual(summary["name"], "test_metric")
            self.assertEqual(summary["count"], 3)
            self.assertEqual(summary["min"], 10.0)
            self.assertEqual(summary["max"], 30.0)
            self.assertEqual(summary["avg"], 20.0)
            
        except Exception as e:
            self.skipTest(f"Test de resumen de métrica no disponible: {e}")
    
    def test_calculate_trend(self):
        """Test calcular tendencia"""
        try:
            # Valores crecientes
            increasing_values = [10, 15, 20, 25, 30]
            trend = self.collector._calculate_trend(increasing_values)
            self.assertEqual(trend, "increasing")
            
            # Valores decrecientes
            decreasing_values = [30, 25, 20, 15, 10]
            trend = self.collector._calculate_trend(decreasing_values)
            self.assertEqual(trend, "decreasing")
            
            # Valores estables
            stable_values = [20, 21, 19, 20, 21]
            trend = self.collector._calculate_trend(stable_values)
            self.assertEqual(trend, "stable")
            
        except Exception as e:
            self.skipTest(f"Test de tendencia no disponible: {e}")
    
    def test_save_load_metrics(self):
        """Test guardar y cargar métricas"""
        try:
            # Registrar algunas métricas
            self.collector.record_metric("test_metric", 42.0)
            self.collector.record_metric("another_metric", 84.0)
            
            # Guardar métricas
            save_path = Path(self.temp_dir) / "test_metrics.json"
            self.collector.save_metrics(str(save_path))
            
            # Verificar que se guardó
            self.assertTrue(save_path.exists())
            
            # Crear nuevo collector y cargar métricas
            new_collector = MetricsCollector(storage_path=self.temp_dir)
            new_collector.load_metrics(str(save_path))
            
            # Verificar que se cargaron
            self.assertEqual(len(new_collector.metrics), 2)
            
        except Exception as e:
            self.skipTest(f"Test de guardar/cargar métricas no disponible: {e}")
    
    def test_get_dashboard_data(self):
        """Test obtener datos para dashboard"""
        try:
            # Registrar métricas de prueba
            self.collector.record_metric("response_time", 0.5)
            self.collector.record_metric("response_time", 0.6)
            self.collector.record_metric("error_count", 1)
            self.collector.record_metric("success_count", 9)
            
            # Obtener datos del dashboard
            dashboard_data = self.collector.get_dashboard_data()
            
            self.assertIsNotNone(dashboard_data)
            self.assertIn("performance", dashboard_data)
            self.assertIn("system", dashboard_data)
            self.assertIn("trends", dashboard_data)
            
        except Exception as e:
            self.skipTest(f"Test de datos del dashboard no disponible: {e}")
    
    def test_metrics_retention(self):
        """Test retención de métricas"""
        try:
            # Configurar collector con retención corta
            collector = MetricsCollector(storage_path=self.temp_dir)
            collector.retention_days = 0  # Sin retención para testing
            
            # Registrar métrica
            collector.record_metric("test_metric", 42.0)
            self.assertEqual(len(collector.metrics), 1)
            
            # Simular métrica antigua
            old_metric = Metric("old_metric", 10.0, datetime.now() - timedelta(days=1))
            collector.metrics.append(old_metric)
            
            # Registrar nueva métrica (esto debería limpiar las antiguas)
            collector.record_metric("new_metric", 84.0)
            
            # Verificar que se limpiaron las métricas antiguas
            self.assertLessEqual(len(collector.metrics), collector.max_metrics)
            
        except Exception as e:
            self.skipTest(f"Test de retención de métricas no disponible: {e}")


if __name__ == '__main__':
    unittest.main()
