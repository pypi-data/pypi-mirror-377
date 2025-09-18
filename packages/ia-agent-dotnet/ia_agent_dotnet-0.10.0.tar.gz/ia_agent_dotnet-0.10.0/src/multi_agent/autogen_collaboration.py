"""
Sistema de colaboración multi-agente con AutoGen
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import asyncio
import json

try:
    from autogen import ConversableAgent, GroupChat, GroupChatManager
    from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
    AUTOGEN_AVAILABLE = True
except ImportError:
    # Fallback para cuando AutoGen no esté disponible
    AUTOGEN_AVAILABLE = False
    ConversableAgent = None
    GroupChat = None
    GroupChatManager = None
    MultimodalConversableAgent = None

from agents.analysis_agent import analysis_agent
from agents.generation_agent import generation_agent
from agents.validation_agent import validation_agent
from agents.optimization_agent import optimization_agent
from agents.coordinator_agent import coordinator_agent
from multi_agent.shared_memory import SharedMemory
from utils.config import Config
from utils.logging import get_logger

logger = get_logger("autogen-collaboration")


class AutoGenAgentWrapper:
    """Wrapper para adaptar nuestros agentes a AutoGen"""
    
    def __init__(self, agent_instance, agent_name: str):
        if not AUTOGEN_AVAILABLE:
            raise ImportError("AutoGen no está disponible. Instala pyautogen para usar esta funcionalidad.")
        
        self.agent_instance = agent_instance
        self.agent_name = agent_name
        self.logger = get_logger(f"autogen-wrapper-{agent_name}")
    
    def generate_reply(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Generar respuesta para AutoGen"""
        try:
            # Obtener el último mensaje
            last_message = messages[-1] if messages else {}
            content = last_message.get("content", "")
            
            # Procesar mensaje con nuestro agente
            if hasattr(self.agent_instance, 'llm') and self.agent_instance.llm:
                response = self.agent_instance.llm.invoke(content)
                return response.content
            else:
                return f"Agente {self.agent_name} procesando: {content}"
                
        except Exception as e:
            self.logger.error(f"Error al generar respuesta: {e}")
            return f"Error en agente {self.agent_name}: {str(e)}"


class MultiAgentCollaboration:
    """Sistema de colaboración multi-agente con AutoGen"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = logger
        
        # Memoria compartida
        self.shared_memory = SharedMemory()
        
        # Agentes AutoGen
        self.autogen_agents: Dict[str, ConversableAgent] = {}
        self.agent_wrappers: Dict[str, AutoGenAgentWrapper] = {}
        
        # Configuración de chat grupal
        self.group_chat = None
        self.group_chat_manager = None
        
        # Estado de colaboración
        self.collaboration_active = False
        self.current_session_id = None
        
        self.logger.info("Sistema de colaboración multi-agente inicializado")
    
    def initialize(self) -> bool:
        """Inicializar sistema de colaboración"""
        try:
            # Inicializar agentes individuales
            self._initialize_individual_agents()
            
            # Crear agentes AutoGen
            self._create_autogen_agents()
            
            # Configurar chat grupal
            self._setup_group_chat()
            
            self.logger.info("Sistema de colaboración inicializado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al inicializar colaboración: {e}")
            return False
    
    def _initialize_individual_agents(self):
        """Inicializar agentes individuales"""
        try:
            # Inicializar cada agente
            agents = [
                ("analysis_agent", analysis_agent),
                ("generation_agent", generation_agent),
                ("validation_agent", validation_agent),
                ("optimization_agent", optimization_agent),
                ("coordinator_agent", coordinator_agent)
            ]
            
            for agent_name, agent_instance in agents:
                if hasattr(agent_instance, 'initialize'):
                    success = agent_instance.initialize()
                    if success:
                        self.logger.info(f"Agente {agent_name} inicializado")
                    else:
                        self.logger.warning(f"Error al inicializar agente {agent_name}")
                
                # Crear wrapper
                wrapper = AutoGenAgentWrapper(agent_instance, agent_name)
                self.agent_wrappers[agent_name] = wrapper
                
        except Exception as e:
            self.logger.error(f"Error al inicializar agentes individuales: {e}")
            raise
    
    def _create_autogen_agents(self):
        """Crear agentes AutoGen"""
        try:
            # Configuración de LLM para AutoGen
            llm_config = {
                "model": self.config.ai.model,
                "temperature": self.config.ai.temperature,
                "api_key": self.config.ai.openai_api_key
            }
            
            # Crear agente analista
            self.autogen_agents["analysis_agent"] = ConversableAgent(
                name="Analista",
                system_message="""
Eres un agente especializado en análisis de código .NET. Tu tarea es:
1. Analizar proyectos .NET y extraer información relevante
2. Identificar patrones de arquitectura y dependencias
3. Proporcionar contexto detallado para la generación de pruebas
4. Colaborar con otros agentes para obtener información completa

Responde de manera clara y estructurada, proporcionando información técnica precisa.
""",
                llm_config=llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=3
            )
            
            # Crear agente generador
            self.autogen_agents["generation_agent"] = ConversableAgent(
                name="Generador",
                system_message="""
Eres un agente especializado en generación de código de pruebas unitarias para .NET. Tu tarea es:
1. Generar pruebas unitarias completas y bien estructuradas
2. Aplicar templates de diferentes frameworks (xUnit, NUnit, MSTest)
3. Crear casos de prueba para happy path, edge cases y error handling
4. Generar mocks y stubs apropiados

Genera código de alta calidad que siga las mejores prácticas de testing.
""",
                llm_config=llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=3
            )
            
            # Crear agente validador
            self.autogen_agents["validation_agent"] = ConversableAgent(
                name="Validador",
                system_message="""
Eres un agente especializado en validación de código y pruebas. Tu tarea es:
1. Validar que el código generado compile correctamente
2. Verificar que las pruebas sigan las mejores prácticas
3. Ejecutar pruebas y reportar resultados
4. Verificar cobertura de código

Proporciona validaciones detalladas y sugerencias de mejora.
""",
                llm_config=llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=3
            )
            
            # Crear agente optimizador
            self.autogen_agents["optimization_agent"] = ConversableAgent(
                name="Optimizador",
                system_message="""
Eres un agente especializado en optimización de código y pruebas. Tu tarea es:
1. Optimizar el rendimiento de las pruebas unitarias
2. Refactorizar código para mejorar legibilidad y mantenibilidad
3. Mejorar la cobertura de código
4. Sugerir mejoras en la estructura de pruebas

Proporciona optimizaciones específicas y accionables.
""",
                llm_config=llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=3
            )
            
            # Crear agente coordinador
            self.autogen_agents["coordinator_agent"] = ConversableAgent(
                name="Coordinador",
                system_message="""
Eres un agente coordinador que gestiona la colaboración entre agentes especializados. Tu tarea es:
1. Coordinar el flujo de trabajo entre agentes
2. Asignar tareas apropiadas a cada agente
3. Sintetizar resultados de múltiples agentes
4. Resolver conflictos y tomar decisiones de coordinación

Mantén el foco en la tarea principal y asegúrate de que todos los agentes trabajen de manera eficiente.
""",
                llm_config=llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=5
            )
            
            self.logger.info("Agentes AutoGen creados exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear agentes AutoGen: {e}")
            raise
    
    def _setup_group_chat(self):
        """Configurar chat grupal"""
        try:
            # Crear lista de agentes para el chat grupal
            agent_list = list(self.autogen_agents.values())
            
            # Crear chat grupal
            self.group_chat = GroupChat(
                agents=agent_list,
                messages=[],
                max_round=10,
                speaker_selection_method="auto"
            )
            
            # Crear manager del chat grupal
            self.group_chat_manager = GroupChatManager(
                groupchat=self.group_chat,
                llm_config={
                    "model": self.config.ai.model,
                    "temperature": self.config.ai.temperature,
                    "api_key": self.config.ai.openai_api_key
                }
            )
            
            self.logger.info("Chat grupal configurado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error al configurar chat grupal: {e}")
            raise
    
    def start_collaboration(self, task_description: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Iniciar sesión de colaboración"""
        try:
            if self.collaboration_active:
                self.logger.warning("Ya hay una colaboración activa")
                return {"success": False, "error": "Colaboración ya activa"}
            
            # Generar ID de sesión si no se proporciona
            if not session_id:
                session_id = f"collab_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.current_session_id = session_id
            self.collaboration_active = True
            
            # Establecer contexto del proyecto en memoria compartida
            self.shared_memory.set_project_context(
                project_id=session_id,
                project_name="Colaboración Multi-Agente",
                project_path="./",
                framework="xunit"
            )
            
            # Iniciar chat grupal
            initial_message = f"""
Tarea de colaboración: {task_description}

Sesión ID: {session_id}
Timestamp: {datetime.now().isoformat()}

Por favor, coordinen entre ustedes para completar esta tarea de manera eficiente.
El Coordinador debe dirigir el flujo de trabajo y asignar tareas apropiadas.
"""
            
            # Ejecutar chat grupal
            result = self.group_chat_manager.initiate_chat(
                message=initial_message,
                recipient=self.autogen_agents["coordinator_agent"]
            )
            
            # Guardar resultado en memoria compartida
            self._save_collaboration_result(session_id, result)
            
            self.logger.info(f"Colaboración completada: {session_id}")
            return {
                "success": True,
                "session_id": session_id,
                "result": result,
                "messages": self.group_chat.messages
            }
            
        except Exception as e:
            self.logger.error(f"Error al iniciar colaboración: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.collaboration_active = False
            self.current_session_id = None
    
    def add_agent_to_collaboration(self, agent_name: str, agent_instance: Any) -> bool:
        """Agregar agente a la colaboración"""
        try:
            if agent_name in self.autogen_agents:
                self.logger.warning(f"Agente {agent_name} ya existe")
                return False
            
            # Crear wrapper
            wrapper = AutoGenAgentWrapper(agent_instance, agent_name)
            self.agent_wrappers[agent_name] = wrapper
            
            # Crear agente AutoGen
            self.autogen_agents[agent_name] = ConversableAgent(
                name=agent_name.replace("_", " ").title(),
                system_message=f"Eres un agente especializado: {agent_name}",
                llm_config={
                    "model": self.config.ai.model,
                    "temperature": self.config.ai.temperature,
                    "api_key": self.config.ai.openai_api_key
                },
                human_input_mode="NEVER",
                max_consecutive_auto_reply=3
            )
            
            # Reconfigurar chat grupal
            self._setup_group_chat()
            
            self.logger.info(f"Agente {agent_name} agregado a la colaboración")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al agregar agente {agent_name}: {e}")
            return False
    
    def remove_agent_from_collaboration(self, agent_name: str) -> bool:
        """Remover agente de la colaboración"""
        try:
            if agent_name not in self.autogen_agents:
                self.logger.warning(f"Agente {agent_name} no existe")
                return False
            
            # Remover agente
            del self.autogen_agents[agent_name]
            if agent_name in self.agent_wrappers:
                del self.agent_wrappers[agent_name]
            
            # Reconfigurar chat grupal
            self._setup_group_chat()
            
            self.logger.info(f"Agente {agent_name} removido de la colaboración")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al remover agente {agent_name}: {e}")
            return False
    
    def get_collaboration_status(self) -> Dict[str, Any]:
        """Obtener estado de la colaboración"""
        return {
            "collaboration_active": self.collaboration_active,
            "current_session_id": self.current_session_id,
            "available_agents": list(self.autogen_agents.keys()),
            "group_chat_configured": self.group_chat is not None,
            "shared_memory_stats": self.shared_memory.get_memory_stats()
        }
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Obtener capacidades de todos los agentes"""
        capabilities = {}
        
        for agent_name, agent_instance in self.agent_wrappers.items():
            if hasattr(agent_instance.agent_instance, 'get_capabilities'):
                capabilities[agent_name] = agent_instance.agent_instance.get_capabilities()
            else:
                capabilities[agent_name] = ["Capacidades no disponibles"]
        
        return capabilities
    
    def _save_collaboration_result(self, session_id: str, result: Any):
        """Guardar resultado de colaboración en memoria compartida"""
        try:
            self.shared_memory.add_entry(
                agent_name="coordinator_agent",
                content=f"Resultado de colaboración para sesión {session_id}",
                entry_type="conversations",
                metadata={
                    "session_id": session_id,
                    "result_type": type(result).__name__,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error al guardar resultado de colaboración: {e}")
    
    def shutdown(self):
        """Apagar sistema de colaboración"""
        try:
            # Apagar agentes individuales
            for agent_name, agent_instance in self.agent_wrappers.items():
                if hasattr(agent_instance.agent_instance, 'shutdown'):
                    agent_instance.agent_instance.shutdown()
            
            # Limpiar estado
            self.autogen_agents.clear()
            self.agent_wrappers.clear()
            self.group_chat = None
            self.group_chat_manager = None
            self.collaboration_active = False
            self.current_session_id = None
            
            self.logger.info("Sistema de colaboración apagado")
            
        except Exception as e:
            self.logger.error(f"Error al apagar sistema de colaboración: {e}")


# Instancia global del sistema de colaboración
multi_agent_collaboration = MultiAgentCollaboration()
