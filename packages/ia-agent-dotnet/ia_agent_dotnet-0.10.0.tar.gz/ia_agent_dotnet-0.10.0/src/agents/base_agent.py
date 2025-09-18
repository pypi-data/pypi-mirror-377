"""
Clase base para agentes del sistema
IA Agent para Generación de Pruebas Unitarias .NET
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime

from utils.config import Config
from utils.logging import get_logger


class AgentStatus(Enum):
    """Estado del agente"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    ERROR = "error"


class AgentRole(Enum):
    """Roles de agentes"""
    ANALYST = "analyst"
    GENERATOR = "generator"
    VALIDATOR = "validator"
    OPTIMIZER = "optimizer"
    COORDINATOR = "coordinator"


@dataclass
class AgentMessage:
    """Mensaje entre agentes"""
    sender: str
    recipient: str
    content: str
    message_type: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentTask:
    """Tarea del agente"""
    task_id: str
    description: str
    priority: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class BaseAgent(ABC):
    """Clase base para todos los agentes del sistema"""
    
    def __init__(self, name: str, role: AgentRole, config: Optional[Config] = None):
        self.name = name
        self.role = role
        self.config = config or Config()
        self.logger = get_logger(f"agent-{name}")
        
        # Estado del agente
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.task_queue: List[AgentTask] = []
        self.message_queue: List[AgentMessage] = []
        
        # Herramientas disponibles
        self.tools: Dict[str, Any] = {}
        
        # Memoria del agente
        self.memory: Optional[Any] = None
        
        # Métricas
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_processing_time = 0.0
        
        self.logger.info(f"Agente {self.name} ({self.role.value}) inicializado")
    
    @abstractmethod
    def initialize(self) -> bool:
        """Inicializar el agente"""
        pass
    
    @abstractmethod
    def process_task(self, task: AgentTask) -> Any:
        """Procesar una tarea"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Obtener capacidades del agente"""
        pass
    
    def add_task(self, task: AgentTask) -> bool:
        """Agregar tarea a la cola"""
        try:
            self.task_queue.append(task)
            self.task_queue.sort(key=lambda t: t.priority, reverse=True)
            self.logger.info(f"Tarea agregada: {task.task_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error al agregar tarea: {e}")
            return False
    
    def get_next_task(self) -> Optional[AgentTask]:
        """Obtener siguiente tarea de la cola"""
        if self.task_queue:
            return self.task_queue.pop(0)
        return None
    
    def send_message(self, recipient: str, content: str, 
                    message_type: str = "general", 
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Enviar mensaje a otro agente"""
        try:
            message = AgentMessage(
                sender=self.name,
                recipient=recipient,
                content=content,
                message_type=message_type,
                timestamp=datetime.now(),
                metadata=metadata
            )
            
            self.message_queue.append(message)
            self.logger.info(f"Mensaje enviado a {recipient}: {message_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje: {e}")
            return False
    
    def receive_message(self) -> Optional[AgentMessage]:
        """Recibir mensaje de la cola"""
        if self.message_queue:
            return self.message_queue.pop(0)
        return None
    
    def set_status(self, status: AgentStatus):
        """Cambiar estado del agente"""
        old_status = self.status
        self.status = status
        self.logger.info(f"Estado cambiado: {old_status.value} -> {status.value}")
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Ejecutar herramienta"""
        try:
            if tool_name not in self.tools:
                raise ValueError(f"Herramienta no disponible: {tool_name}")
            
            tool = self.tools[tool_name]
            self.logger.info(f"Ejecutando herramienta: {tool_name}")
            
            # Ejecutar herramienta
            if asyncio.iscoroutinefunction(tool):
                result = asyncio.run(tool(**kwargs))
            else:
                result = tool(**kwargs)
            
            self.logger.info(f"Herramienta {tool_name} ejecutada exitosamente")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al ejecutar herramienta {tool_name}: {e}")
            raise
    
    def update_memory(self, key: str, value: Any):
        """Actualizar memoria del agente"""
        try:
            if self.memory:
                self.memory.update(key, value)
                self.logger.debug(f"Memoria actualizada: {key}")
        except Exception as e:
            self.logger.error(f"Error al actualizar memoria: {e}")
    
    def get_memory(self, key: str) -> Any:
        """Obtener valor de memoria"""
        try:
            if self.memory:
                return self.memory.get(key)
            return None
        except Exception as e:
            self.logger.error(f"Error al obtener memoria: {e}")
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del agente"""
        return {
            'name': self.name,
            'role': self.role.value,
            'status': self.status.value,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_processing_time': self.total_processing_time,
            'queue_size': len(self.task_queue),
            'message_queue_size': len(self.message_queue),
            'tools_available': list(self.tools.keys())
        }
    
    def reset_metrics(self):
        """Resetear métricas"""
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_processing_time = 0.0
        self.logger.info("Métricas reseteadas")
    
    def shutdown(self):
        """Apagar el agente"""
        try:
            self.set_status(AgentStatus.IDLE)
            self.task_queue.clear()
            self.message_queue.clear()
            self.logger.info(f"Agente {self.name} apagado")
        except Exception as e:
            self.logger.error(f"Error al apagar agente: {e}")


class ReActAgent(BaseAgent):
    """Agente con capacidades ReAct (Reasoning and Acting)"""
    
    def __init__(self, name: str, role: AgentRole, config: Optional[Config] = None):
        super().__init__(name, role, config)
        self.reasoning_history: List[Dict[str, Any]] = []
        self.action_history: List[Dict[str, Any]] = []
    
    def reason(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fase de razonamiento"""
        try:
            self.set_status(AgentStatus.THINKING)
            self.logger.info("Iniciando fase de razonamiento")
            
            # Analizar contexto
            analysis = self._analyze_context(context)
            
            # Identificar acciones necesarias
            actions = self._identify_actions(analysis)
            
            # Priorizar acciones
            prioritized_actions = self._prioritize_actions(actions)
            
            reasoning_result = {
                'context_analysis': analysis,
                'identified_actions': actions,
                'prioritized_actions': prioritized_actions,
                'timestamp': datetime.now()
            }
            
            self.reasoning_history.append(reasoning_result)
            self.logger.info("Fase de razonamiento completada")
            
            return reasoning_result
            
        except Exception as e:
            self.logger.error(f"Error en fase de razonamiento: {e}")
            raise
    
    def act(self, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fase de actuación"""
        try:
            self.set_status(AgentStatus.ACTING)
            self.logger.info("Iniciando fase de actuación")
            
            actions = reasoning_result.get('prioritized_actions', [])
            results = []
            
            for action in actions:
                try:
                    result = self._execute_action(action)
                    results.append({
                        'action': action,
                        'result': result,
                        'success': True
                    })
                except Exception as e:
                    self.logger.error(f"Error al ejecutar acción {action}: {e}")
                    results.append({
                        'action': action,
                        'result': None,
                        'success': False,
                        'error': str(e)
                    })
            
            action_result = {
                'actions_executed': results,
                'timestamp': datetime.now()
            }
            
            self.action_history.append(action_result)
            self.logger.info("Fase de actuación completada")
            
            return action_result
            
        except Exception as e:
            self.logger.error(f"Error en fase de actuación: {e}")
            raise
    
    def observe(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fase de observación"""
        try:
            self.logger.info("Iniciando fase de observación")
            
            # Analizar resultados de acciones
            observation = self._analyze_action_results(action_result)
            
            # Determinar próximos pasos
            next_steps = self._determine_next_steps(observation)
            
            observation_result = {
                'observation': observation,
                'next_steps': next_steps,
                'timestamp': datetime.now()
            }
            
            self.logger.info("Fase de observación completada")
            return observation_result
            
        except Exception as e:
            self.logger.error(f"Error en fase de observación: {e}")
            raise
    
    def react_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar ciclo completo ReAct"""
        try:
            self.logger.info("Iniciando ciclo ReAct")
            
            # Reasoning
            reasoning_result = self.reason(context)
            
            # Acting
            action_result = self.act(reasoning_result)
            
            # Observation
            observation_result = self.observe(action_result)
            
            cycle_result = {
                'reasoning': reasoning_result,
                'acting': action_result,
                'observation': observation_result,
                'timestamp': datetime.now()
            }
            
            self.logger.info("Ciclo ReAct completado")
            return cycle_result
            
        except Exception as e:
            self.logger.error(f"Error en ciclo ReAct: {e}")
            raise
    
    @abstractmethod
    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar contexto específico del agente"""
        pass
    
    @abstractmethod
    def _identify_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identificar acciones necesarias"""
        pass
    
    def _prioritize_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Priorizar acciones"""
        # Implementación básica de priorización
        return sorted(actions, key=lambda x: x.get('priority', 0), reverse=True)
    
    @abstractmethod
    def _execute_action(self, action: Dict[str, Any]) -> Any:
        """Ejecutar acción específica"""
        pass
    
    def _analyze_action_results(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar resultados de acciones"""
        results = action_result.get('actions_executed', [])
        
        successful_actions = [r for r in results if r.get('success', False)]
        failed_actions = [r for r in results if not r.get('success', False)]
        
        return {
            'total_actions': len(results),
            'successful_actions': len(successful_actions),
            'failed_actions': len(failed_actions),
            'success_rate': len(successful_actions) / len(results) if results else 0
        }
    
    def _determine_next_steps(self, observation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determinar próximos pasos basados en observación"""
        # Implementación básica
        if observation.get('success_rate', 0) < 0.8:
            return [{'action': 'retry_failed_actions', 'priority': 1}]
        
        return [{'action': 'continue', 'priority': 0}]
