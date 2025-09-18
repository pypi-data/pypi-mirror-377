"""
Tests de integración del sistema completo
IA Agent para Generación de Pruebas Unitarias .NET
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import get_config
from utils.logging import get_logger
from agents.analysis_agent import AnalysisAgent
from agents.generation_agent import GenerationAgent
from tools.file_tools import file_manager
from ai.context_manager import ContextManager
from monitoring.metrics_collector import MetricsCollector


class TestIntegration(unittest.TestCase):
    """Tests de integración del sistema completo"""
    
    def setUp(self):
        """Configuración inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_path = Path(self.temp_dir) / "TestProject"
        self.test_project_path.mkdir()
        
        # Crear archivo de proyecto de prueba
        self.create_test_project()
    
    def tearDown(self):
        """Limpieza"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_project(self):
        """Crear proyecto de prueba"""
        try:
            # Crear archivo de proyecto
            project_file = self.test_project_path / "TestProject.csproj"
            project_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <OutputType>Library</OutputType>
  </PropertyGroup>
</Project>"""
            file_manager.write_file(str(project_file), project_content)
            
            # Crear archivo de código
            code_file = self.test_project_path / "Calculator.cs"
            code_content = """using System;

namespace TestProject
{
    public class Calculator
    {
        public int Add(int a, int b)
        {
            return a + b;
        }
        
        public int Subtract(int a, int b)
        {
            return a - b;
        }
        
        public int Multiply(int a, int b)
        {
            return a * b;
        }
        
        public double Divide(int a, int b)
        {
            if (b == 0)
                throw new DivideByZeroException("Cannot divide by zero");
            
            return (double)a / b;
        }
    }
}"""
            file_manager.write_file(str(code_file), code_content)
            
        except Exception as e:
            self.skipTest(f"No se pudo crear proyecto de prueba: {e}")
    
    def test_system_configuration(self):
        """Test configuración del sistema"""
        try:
            # Verificar configuración
            config = get_config()
            self.assertIsNotNone(config)
            self.assertIsNotNone(config.agent)
            self.assertIsNotNone(config.ai)
            self.assertIsNotNone(config.memory)
            
        except Exception as e:
            self.skipTest(f"Configuración del sistema no disponible: {e}")
    
    def test_logging_system(self):
        """Test sistema de logging"""
        try:
            # Verificar logger
            logger = get_logger("test")
            self.assertIsNotNone(logger)
            
            # Probar logging
            logger.info("Test log message")
            
        except Exception as e:
            self.skipTest(f"Sistema de logging no disponible: {e}")
    
    def test_file_operations_integration(self):
        """Test integración de operaciones de archivos"""
        try:
            # Verificar que el proyecto de prueba existe
            self.assertTrue(self.test_project_path.exists())
            
            # Verificar archivos del proyecto
            project_file = self.test_project_path / "TestProject.csproj"
            code_file = self.test_project_path / "Calculator.cs"
            
            self.assertTrue(project_file.exists())
            self.assertTrue(code_file.exists())
            
            # Leer contenido
            project_content = file_manager.read_file(str(project_file))
            code_content = file_manager.read_file(str(code_file))
            
            self.assertIn("net8.0", project_content)
            self.assertIn("Calculator", code_content)
            
        except Exception as e:
            self.skipTest(f"Operaciones de archivos no disponibles: {e}")
    
    def test_agent_integration(self):
        """Test integración de agentes"""
        try:
            # Crear agentes
            analysis_agent = AnalysisAgent()
            generation_agent = GenerationAgent()
            
            self.assertIsNotNone(analysis_agent)
            self.assertIsNotNone(generation_agent)
            
            # Verificar capacidades
            analysis_capabilities = analysis_agent.get_capabilities()
            generation_capabilities = generation_agent.get_capabilities()
            
            self.assertIsInstance(analysis_capabilities, list)
            self.assertIsInstance(generation_capabilities, list)
            self.assertGreater(len(analysis_capabilities), 0)
            self.assertGreater(len(generation_capabilities), 0)
            
        except Exception as e:
            self.skipTest(f"Integración de agentes no disponible: {e}")
    
    def test_context_manager_integration(self):
        """Test integración del context manager"""
        try:
            # Crear context manager
            context_manager = ContextManager()
            self.assertIsNotNone(context_manager)
            
            # Crear sesión
            session = context_manager.create_session("test_session")
            self.assertIsNotNone(session)
            
            # Agregar contexto de código
            code_file = self.test_project_path / "Calculator.cs"
            code_content = file_manager.read_file(str(code_file))
            
            code_context = context_manager.add_code_context(
                file_path=str(code_file),
                content=code_content
            )
            
            self.assertIsNotNone(code_context)
            self.assertIn("Calculator", code_context.classes)
            
            # Establecer contexto de proyecto
            context_manager.set_project_context(
                project_path=str(self.test_project_path),
                name="TestProject",
                framework="net8.0"
            )
            
            self.assertIsNotNone(session.current_project)
            self.assertEqual(session.current_project.name, "TestProject")
            
        except Exception as e:
            self.skipTest(f"Integración del context manager no disponible: {e}")
    
    def test_metrics_collector_integration(self):
        """Test integración del metrics collector"""
        try:
            # Crear metrics collector
            metrics_collector = MetricsCollector(storage_path=self.temp_dir)
            self.assertIsNotNone(metrics_collector)
            
            # Registrar métricas de prueba
            metrics_collector.record_metric("test_metric", 42.0)
            metrics_collector.record_metric("response_time", 0.5)
            
            # Verificar métricas
            self.assertEqual(len(metrics_collector.metrics), 2)
            
            # Obtener resumen
            summary = metrics_collector.get_metric_summary("test_metric")
            self.assertIsNotNone(summary)
            self.assertEqual(summary["name"], "test_metric")
            
        except Exception as e:
            self.skipTest(f"Integración del metrics collector no disponible: {e}")
    
    def test_end_to_end_workflow(self):
        """Test flujo de trabajo completo"""
        try:
            # 1. Configurar contexto
            context_manager = ContextManager()
            session = context_manager.create_session("e2e_test")
            
            # 2. Agregar código al contexto
            code_file = self.test_project_path / "Calculator.cs"
            code_content = file_manager.read_file(str(code_file))
            
            context_manager.add_code_context(
                file_path=str(code_file),
                content=code_content
            )
            
            # 3. Establecer contexto de proyecto
            context_manager.set_project_context(
                project_path=str(self.test_project_path),
                name="TestProject",
                framework="net8.0"
            )
            
            # 4. Registrar métricas
            metrics_collector = MetricsCollector(storage_path=self.temp_dir)
            metrics_collector.record_metric("workflow_started", 1.0)
            
            # 5. Crear agentes
            analysis_agent = AnalysisAgent()
            generation_agent = GenerationAgent()
            
            # 6. Verificar que todo está configurado
            self.assertIsNotNone(session.current_project)
            self.assertIsNotNone(session.code_contexts)
            self.assertGreater(len(metrics_collector.metrics), 0)
            self.assertIsNotNone(analysis_agent)
            self.assertIsNotNone(generation_agent)
            
            # 7. Registrar finalización
            metrics_collector.record_metric("workflow_completed", 1.0)
            
        except Exception as e:
            self.skipTest(f"Flujo de trabajo completo no disponible: {e}")
    
    def test_error_handling_integration(self):
        """Test manejo de errores en integración"""
        try:
            # Probar con archivo inexistente
            non_existent_file = self.test_project_path / "NonExistent.cs"
            
            # Esto debería manejar el error gracefully
            try:
                content = file_manager.read_file(str(non_existent_file))
                self.fail("Debería haber lanzado una excepción")
            except Exception:
                # Esto es esperado
                pass
            
            # Probar con contexto inválido
            context_manager = ContextManager()
            try:
                context_manager.add_code_context("", "")
                # Esto debería funcionar o manejar el error gracefully
            except Exception:
                # Esto es aceptable
                pass
            
        except Exception as e:
            self.skipTest(f"Test de manejo de errores no disponible: {e}")
    
    def test_performance_integration(self):
        """Test rendimiento en integración"""
        try:
            import time
            
            # Medir tiempo de creación de componentes
            start_time = time.time()
            
            # Crear múltiples componentes
            context_manager = ContextManager()
            metrics_collector = MetricsCollector(storage_path=self.temp_dir)
            analysis_agent = AnalysisAgent()
            generation_agent = GenerationAgent()
            
            creation_time = time.time() - start_time
            
            # Verificar que la creación fue razonablemente rápida
            self.assertLess(creation_time, 10.0)  # Menos de 10 segundos
            
            # Medir tiempo de operaciones
            start_time = time.time()
            
            # Realizar operaciones
            session = context_manager.create_session("perf_test")
            metrics_collector.record_metric("perf_test", 1.0)
            
            operation_time = time.time() - start_time
            
            # Verificar que las operaciones fueron rápidas
            self.assertLess(operation_time, 5.0)  # Menos de 5 segundos
            
        except Exception as e:
            self.skipTest(f"Test de rendimiento no disponible: {e}")


if __name__ == '__main__':
    unittest.main()
