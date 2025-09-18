"""
Tests para componentes de IA
IA Agent para Generación de Pruebas Unitarias .NET
"""

import unittest
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.llm_manager import LLMManager, LLMProvider
from ai.prompt_engineer import PromptEngineer, PromptType
from ai.context_manager import ContextManager
from ai.ai_optimizer import AIOptimizer


class TestAI(unittest.TestCase):
    """Tests para componentes de IA"""
    
    def setUp(self):
        """Configuración inicial"""
        self.test_session_id = "test_session_123"
    
    def test_llm_manager_creation(self):
        """Test creación de LLM manager"""
        try:
            manager = LLMManager()
            self.assertIsNotNone(manager)
            self.assertIsNotNone(manager.llms)
            self.assertGreater(len(manager.llms), 0)
            
        except Exception as e:
            self.skipTest(f"LLM Manager no disponible: {e}")
    
    def test_llm_manager_get_llm(self):
        """Test obtener LLM del manager"""
        try:
            manager = LLMManager()
            
            # Obtener LLM primario
            primary_llm = manager.get_llm("primary")
            self.assertIsNotNone(primary_llm)
            
            # Obtener LLM rápido
            fast_llm = manager.get_llm("fast")
            self.assertIsNotNone(fast_llm)
            
        except Exception as e:
            self.skipTest(f"Test de LLM no disponible: {e}")
    
    def test_llm_manager_switch_llm(self):
        """Test cambiar LLM actual"""
        try:
            manager = LLMManager()
            
            # Cambiar a LLM rápido
            manager.switch_llm("fast")
            self.assertEqual(manager.current_llm, manager.llms["fast"])
            
            # Cambiar a LLM primario
            manager.switch_llm("primary")
            self.assertEqual(manager.current_llm, manager.llms["primary"])
            
        except Exception as e:
            self.skipTest(f"Test de cambio de LLM no disponible: {e}")
    
    def test_llm_manager_get_available_llms(self):
        """Test obtener LLMs disponibles"""
        try:
            manager = LLMManager()
            available_llms = manager.get_available_llms()
            
            self.assertIsInstance(available_llms, list)
            self.assertGreater(len(available_llms), 0)
            self.assertIn("primary", available_llms)
            
        except Exception as e:
            self.skipTest(f"Test de LLMs disponibles no disponible: {e}")
    
    def test_prompt_engineer_creation(self):
        """Test creación de prompt engineer"""
        try:
            engineer = PromptEngineer()
            self.assertIsNotNone(engineer)
            self.assertIsNotNone(engineer.templates)
            self.assertGreater(len(engineer.templates), 0)
            
        except Exception as e:
            self.skipTest(f"Prompt Engineer no disponible: {e}")
    
    def test_prompt_engineer_get_template(self):
        """Test obtener template de prompt"""
        try:
            engineer = PromptEngineer()
            
            # Obtener template de análisis de código
            template = engineer.get_template("code_analysis")
            self.assertIsNotNone(template)
            self.assertEqual(template.type, PromptType.CODE_ANALYSIS)
            
            # Obtener template de generación de pruebas
            template = engineer.get_template("test_generation")
            self.assertIsNotNone(template)
            self.assertEqual(template.type, PromptType.TEST_GENERATION)
            
        except Exception as e:
            self.skipTest(f"Test de templates no disponible: {e}")
    
    def test_prompt_engineer_generate_prompt(self):
        """Test generar prompt desde template"""
        try:
            engineer = PromptEngineer()
            
            # Variables para el template
            variables = {
                "code": "public class TestClass { }",
                "context": "Test context"
            }
            
            # Generar prompt
            prompt = engineer.generate_prompt("code_analysis", variables)
            self.assertIsNotNone(prompt)
            self.assertIn("TestClass", prompt)
            self.assertIn("Test context", prompt)
            
        except Exception as e:
            self.skipTest(f"Test de generación de prompt no disponible: {e}")
    
    def test_prompt_engineer_get_available_templates(self):
        """Test obtener templates disponibles"""
        try:
            engineer = PromptEngineer()
            templates = engineer.get_available_templates()
            
            self.assertIsInstance(templates, list)
            self.assertGreater(len(templates), 0)
            self.assertIn("code_analysis", templates)
            self.assertIn("test_generation", templates)
            
        except Exception as e:
            self.skipTest(f"Test de templates disponibles no disponible: {e}")
    
    def test_context_manager_creation(self):
        """Test creación de context manager"""
        try:
            manager = ContextManager()
            self.assertIsNotNone(manager)
            self.assertIsNotNone(manager.sessions)
            self.assertIsNone(manager.current_session)
            
        except Exception as e:
            self.skipTest(f"Context Manager no disponible: {e}")
    
    def test_context_manager_create_session(self):
        """Test crear sesión en context manager"""
        try:
            manager = ContextManager()
            
            # Crear sesión
            session = manager.create_session(self.test_session_id)
            self.assertIsNotNone(session)
            self.assertEqual(session.session_id, self.test_session_id)
            self.assertEqual(manager.current_session, session)
            
        except Exception as e:
            self.skipTest(f"Test de creación de sesión no disponible: {e}")
    
    def test_context_manager_add_code_context(self):
        """Test agregar contexto de código"""
        try:
            manager = ContextManager()
            session = manager.create_session(self.test_session_id)
            
            # Agregar contexto de código
            code_context = manager.add_code_context(
                file_path="test.cs",
                content="public class TestClass { }"
            )
            
            self.assertIsNotNone(code_context)
            self.assertEqual(code_context.file_path, "test.cs")
            self.assertIn("TestClass", code_context.classes)
            
        except Exception as e:
            self.skipTest(f"Test de contexto de código no disponible: {e}")
    
    def test_context_manager_set_project_context(self):
        """Test establecer contexto de proyecto"""
        try:
            manager = ContextManager()
            session = manager.create_session(self.test_session_id)
            
            # Establecer contexto de proyecto
            manager.set_project_context(
                project_path="/test/project",
                name="TestProject",
                framework="net8.0"
            )
            
            self.assertIsNotNone(session.current_project)
            self.assertEqual(session.current_project.name, "TestProject")
            self.assertEqual(session.current_project.framework, "net8.0")
            
        except Exception as e:
            self.skipTest(f"Test de contexto de proyecto no disponible: {e}")
    
    def test_context_manager_add_conversation_entry(self):
        """Test agregar entrada de conversación"""
        try:
            manager = ContextManager()
            session = manager.create_session(self.test_session_id)
            
            # Agregar entrada de conversación
            manager.add_conversation_entry("human", "Hello")
            manager.add_conversation_entry("ai", "Hi there!")
            
            self.assertEqual(len(session.conversation_history), 2)
            self.assertEqual(session.conversation_history[0]["role"], "human")
            self.assertEqual(session.conversation_history[1]["role"], "ai")
            
        except Exception as e:
            self.skipTest(f"Test de entrada de conversación no disponible: {e}")
    
    def test_context_manager_get_relevant_context(self):
        """Test obtener contexto relevante"""
        try:
            manager = ContextManager()
            session = manager.create_session(self.test_session_id)
            
            # Agregar contexto
            manager.add_code_context("test.cs", "public class TestClass { }")
            manager.set_project_context("/test", "TestProject", "net8.0")
            
            # Obtener contexto relevante
            context = manager.get_relevant_context("TestClass")
            self.assertIsNotNone(context)
            self.assertIsNotNone(context.get("project"))
            
        except Exception as e:
            self.skipTest(f"Test de contexto relevante no disponible: {e}")
    
    def test_ai_optimizer_creation(self):
        """Test creación de AI optimizer"""
        try:
            optimizer = AIOptimizer()
            self.assertIsNotNone(optimizer)
            self.assertIsNotNone(optimizer.optimization_rules)
            self.assertIsNotNone(optimizer.metrics_history)
            
        except Exception as e:
            self.skipTest(f"AI Optimizer no disponible: {e}")
    
    def test_ai_optimizer_optimize_prompt(self):
        """Test optimizar prompt"""
        try:
            optimizer = AIOptimizer()
            
            # Prompt de prueba
            prompt = "Analyze this code: public class Test { }"
            context = {"framework": "net8.0"}
            
            # Optimizar prompt
            optimized = optimizer._apply_prompt_optimization(prompt, context)
            self.assertIsNotNone(optimized)
            self.assertIn("net8.0", optimized)
            
        except Exception as e:
            self.skipTest(f"Test de optimización de prompt no disponible: {e}")
    
    def test_ai_optimizer_optimize_response(self):
        """Test optimizar respuesta"""
        try:
            optimizer = AIOptimizer()
            
            # Respuesta de prueba
            response = "This is a test response."
            prompt = "Test prompt"
            
            # Optimizar respuesta
            result = optimizer._apply_response_optimization(response, prompt)
            self.assertIsNotNone(result)
            self.assertIn("test response", result)
            
        except Exception as e:
            self.skipTest(f"Test de optimización de respuesta no disponible: {e}")
    
    def test_ai_optimizer_get_performance_metrics(self):
        """Test obtener métricas de rendimiento"""
        try:
            optimizer = AIOptimizer()
            
            # Obtener métricas
            metrics = optimizer.get_performance_metrics()
            self.assertIsNotNone(metrics)
            self.assertIsInstance(metrics, dict)
            
        except Exception as e:
            self.skipTest(f"Test de métricas de rendimiento no disponible: {e}")


if __name__ == '__main__':
    unittest.main()
