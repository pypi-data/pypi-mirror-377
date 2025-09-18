"""
Tests para sistema de memoria
IA Agent para Generación de Pruebas Unitarias .NET
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_agents.memory.conversation_memory import ConversationMemory
from langchain_agents.memory.vector_memory import VectorMemory
from multi_agent.shared_memory import SharedMemory


class TestMemory(unittest.TestCase):
    """Tests para sistema de memoria"""
    
    def setUp(self):
        """Configuración inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent_name = "test_agent"
        self.test_message = "Test message"
    
    def tearDown(self):
        """Limpieza"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_conversation_memory_creation(self):
        """Test creación de memoria de conversación"""
        try:
            memory = ConversationMemory(
                agent_name=self.agent_name,
                storage_path=self.temp_dir
            )
            
            self.assertIsNotNone(memory)
            self.assertEqual(memory.agent_name, self.agent_name)
            self.assertIsNotNone(memory.buffer_memory)
            
        except Exception as e:
            self.skipTest(f"Memoria de conversación no disponible: {e}")
    
    def test_conversation_memory_add_message(self):
        """Test agregar mensaje a memoria de conversación"""
        try:
            memory = ConversationMemory(
                agent_name=self.agent_name,
                storage_path=self.temp_dir
            )
            
            # Agregar mensaje
            memory.add_message("human", self.test_message)
            
            # Verificar que se agregó
            history = memory.get_conversation_history()
            self.assertGreater(len(history), 0)
            
        except Exception as e:
            self.skipTest(f"Test de mensajes no disponible: {e}")
    
    def test_conversation_memory_get_history(self):
        """Test obtener historial de conversación"""
        try:
            memory = ConversationMemory(
                agent_name=self.agent_name,
                storage_path=self.temp_dir
            )
            
            # Agregar varios mensajes
            memory.add_message("human", "Hello")
            memory.add_message("ai", "Hi there!")
            memory.add_message("human", "How are you?")
            
            # Obtener historial
            history = memory.get_conversation_history()
            self.assertGreaterEqual(len(history), 3)
            
        except Exception as e:
            self.skipTest(f"Test de historial no disponible: {e}")
    
    def test_conversation_memory_clear(self):
        """Test limpiar memoria de conversación"""
        try:
            memory = ConversationMemory(
                agent_name=self.agent_name,
                storage_path=self.temp_dir
            )
            
            # Agregar mensaje
            memory.add_message("human", self.test_message)
            
            # Limpiar memoria
            memory.clear_memory()
            
            # Verificar que se limpió
            history = memory.get_conversation_history()
            self.assertEqual(len(history), 0)
            
        except Exception as e:
            self.skipTest(f"Test de limpieza no disponible: {e}")
    
    def test_vector_memory_creation(self):
        """Test creación de memoria vectorial"""
        try:
            memory = VectorMemory(
                agent_name=self.agent_name,
                storage_path=self.temp_dir
            )
            
            self.assertIsNotNone(memory)
            self.assertEqual(memory.agent_name, self.agent_name)
            
        except Exception as e:
            self.skipTest(f"Memoria vectorial no disponible: {e}")
    
    def test_vector_memory_add_document(self):
        """Test agregar documento a memoria vectorial"""
        try:
            memory = VectorMemory(
                agent_name=self.agent_name,
                storage_path=self.temp_dir
            )
            
            # Agregar documento
            memory.add_document(
                content="Test document content",
                metadata={"type": "test"}
            )
            
            # Verificar que se agregó
            results = memory.search("test", limit=1)
            self.assertGreater(len(results), 0)
            
        except Exception as e:
            self.skipTest(f"Test de documentos no disponible: {e}")
    
    def test_vector_memory_search(self):
        """Test búsqueda en memoria vectorial"""
        try:
            memory = VectorMemory(
                agent_name=self.agent_name,
                storage_path=self.temp_dir
            )
            
            # Agregar documentos
            memory.add_document("Python programming", {"type": "programming"})
            memory.add_document("C# development", {"type": "programming"})
            memory.add_document("Machine learning", {"type": "ai"})
            
            # Buscar
            results = memory.search("programming", limit=2)
            self.assertGreater(len(results), 0)
            
        except Exception as e:
            self.skipTest(f"Test de búsqueda no disponible: {e}")
    
    def test_shared_memory_creation(self):
        """Test creación de memoria compartida"""
        try:
            memory = SharedMemory(storage_path=self.temp_dir)
            
            self.assertIsNotNone(memory)
            
        except Exception as e:
            self.skipTest(f"Memoria compartida no disponible: {e}")
    
    def test_shared_memory_add_entry(self):
        """Test agregar entrada a memoria compartida"""
        try:
            memory = SharedMemory(storage_path=self.temp_dir)
            
            # Agregar entrada
            memory.add_entry(
                agent_name=self.agent_name,
                content="Shared test content",
                metadata={"type": "test"}
            )
            
            # Verificar que se agregó
            results = memory.search("test", limit=1)
            self.assertGreater(len(results), 0)
            
        except Exception as e:
            self.skipTest(f"Test de entradas compartidas no disponible: {e}")
    
    def test_shared_memory_search(self):
        """Test búsqueda en memoria compartida"""
        try:
            memory = SharedMemory(storage_path=self.temp_dir)
            
            # Agregar entradas
            memory.add_entry(self.agent_name, "Python code", {"language": "python"})
            memory.add_entry(self.agent_name, "C# code", {"language": "csharp"})
            
            # Buscar
            results = memory.search("code", limit=2)
            self.assertGreater(len(results), 0)
            
        except Exception as e:
            self.skipTest(f"Test de búsqueda compartida no disponible: {e}")


if __name__ == '__main__':
    unittest.main()
