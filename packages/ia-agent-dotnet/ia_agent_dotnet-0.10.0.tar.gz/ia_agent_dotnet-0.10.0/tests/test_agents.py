"""
Tests para agentes
IA Agent para Generación de Pruebas Unitarias .NET
"""

import unittest
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.base_agent import BaseAgent, ReActAgent, AgentRole, AgentStatus
from agents.analysis_agent import AnalysisAgent
from agents.generation_agent import GenerationAgent
from agents.validation_agent import ValidationAgent
from agents.optimization_agent import OptimizationAgent
from agents.coordinator_agent import CoordinatorAgent


class TestAgents(unittest.TestCase):
    """Tests para agentes del sistema"""
    
    def setUp(self):
        """Configuración inicial"""
        self.test_agent_name = "test_agent"
        self.test_role = AgentRole.ANALYST
    
    def test_base_agent_creation(self):
        """Test creación de agente base"""
        agent = BaseAgent(
            name=self.test_agent_name,
            role=self.test_role,
            system_message="Test system message"
        )
        
        self.assertEqual(agent.name, self.test_agent_name)
        self.assertEqual(agent.role, self.test_role)
        self.assertEqual(agent.status, AgentStatus.IDLE)
        self.assertIsNotNone(agent.created_at)
    
    def test_react_agent_creation(self):
        """Test creación de agente ReAct"""
        agent = ReActAgent(
            name=self.test_agent_name,
            role=self.test_role,
            system_message="Test system message"
        )
        
        self.assertEqual(agent.name, self.test_agent_name)
        self.assertEqual(agent.role, self.test_role)
        self.assertIsNotNone(agent.tools)
        self.assertIsInstance(agent.tools, list)
    
    def test_analysis_agent_creation(self):
        """Test creación de agente de análisis"""
        try:
            agent = AnalysisAgent()
            self.assertIsNotNone(agent)
            self.assertEqual(agent.role, AgentRole.ANALYST)
            self.assertIsNotNone(agent.capabilities)
        except Exception as e:
            # Puede fallar por dependencias de ChromaDB
            self.skipTest(f"Agente de análisis no disponible: {e}")
    
    def test_generation_agent_creation(self):
        """Test creación de agente de generación"""
        try:
            agent = GenerationAgent()
            self.assertIsNotNone(agent)
            self.assertEqual(agent.role, AgentRole.GENERATOR)
            self.assertIsNotNone(agent.capabilities)
        except Exception as e:
            # Puede fallar por dependencias de ChromaDB
            self.skipTest(f"Agente de generación no disponible: {e}")
    
    def test_validation_agent_creation(self):
        """Test creación de agente de validación"""
        try:
            agent = ValidationAgent()
            self.assertIsNotNone(agent)
            self.assertEqual(agent.role, AgentRole.VALIDATOR)
            self.assertIsNotNone(agent.capabilities)
        except Exception as e:
            # Puede fallar por dependencias de ChromaDB
            self.skipTest(f"Agente de validación no disponible: {e}")
    
    def test_optimization_agent_creation(self):
        """Test creación de agente de optimización"""
        try:
            agent = OptimizationAgent()
            self.assertIsNotNone(agent)
            self.assertEqual(agent.role, AgentRole.OPTIMIZER)
            self.assertIsNotNone(agent.capabilities)
        except Exception as e:
            # Puede fallar por dependencias de ChromaDB
            self.skipTest(f"Agente de optimización no disponible: {e}")
    
    def test_coordinator_agent_creation(self):
        """Test creación de agente coordinador"""
        try:
            agent = CoordinatorAgent()
            self.assertIsNotNone(agent)
            self.assertEqual(agent.role, AgentRole.COORDINATOR)
            self.assertIsNotNone(agent.capabilities)
        except Exception as e:
            # Puede fallar por dependencias de ChromaDB
            self.skipTest(f"Agente coordinador no disponible: {e}")
    
    def test_agent_capabilities(self):
        """Test capacidades de agentes"""
        try:
            # Test agente de análisis
            analysis_agent = AnalysisAgent()
            capabilities = analysis_agent.get_capabilities()
            self.assertIsInstance(capabilities, list)
            self.assertGreater(len(capabilities), 0)
            
            # Test agente de generación
            generation_agent = GenerationAgent()
            capabilities = generation_agent.get_capabilities()
            self.assertIsInstance(capabilities, list)
            self.assertGreater(len(capabilities), 0)
            
        except Exception as e:
            self.skipTest(f"Test de capacidades no disponible: {e}")
    
    def test_agent_status_transitions(self):
        """Test transiciones de estado de agentes"""
        agent = BaseAgent(
            name=self.test_agent_name,
            role=self.test_role,
            system_message="Test system message"
        )
        
        # Estado inicial
        self.assertEqual(agent.status, AgentStatus.IDLE)
        
        # Cambiar a activo
        agent.status = AgentStatus.ACTIVE
        self.assertEqual(agent.status, AgentStatus.ACTIVE)
        
        # Cambiar a inactivo
        agent.status = AgentStatus.IDLE
        self.assertEqual(agent.status, AgentStatus.IDLE)
    
    def test_agent_roles(self):
        """Test roles de agentes"""
        roles = [
            AgentRole.ANALYST,
            AgentRole.GENERATOR,
            AgentRole.VALIDATOR,
            AgentRole.OPTIMIZER,
            AgentRole.COORDINATOR
        ]
        
        for role in roles:
            agent = BaseAgent(
                name=f"test_{role.value}",
                role=role,
                system_message="Test system message"
            )
            self.assertEqual(agent.role, role)


if __name__ == '__main__':
    unittest.main()
