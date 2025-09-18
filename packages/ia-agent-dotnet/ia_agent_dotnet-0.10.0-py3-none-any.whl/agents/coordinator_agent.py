"""
Agente Coordinador - Coordina la colaboración entre agentes
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from agents.base_agent import ReActAgent, AgentRole, AgentTask, AgentMessage
from langchain_agents.memory.conversation_memory import ConversationMemory
from langchain_agents.memory.vector_memory import VectorMemory
from multi_agent.shared_memory import SharedMemory
from utils.config import Config
from utils.logging import get_logger

logger = get_logger("coordinator-agent")


class CoordinatorAgent(ReActAgent):
    """Agente coordinador para la colaboración multi-agente"""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__("coordinator_agent", AgentRole.COORDINATOR, config)
        
        self.logger = logger
        self.llm = None
        self.agent_executor = None
        
        # Memoria del agente
        self.conversation_memory = ConversationMemory("coordinator_agent")
        self.vector_memory = VectorMemory("coordinator_agent")
        
        # Memoria compartida
        self.shared_memory = SharedMemory()
        
        # Agentes disponibles
        self.available_agents: Dict[str, Any] = {}
        self.agent_status: Dict[str, str] = {}
        
        # Cola de tareas global
        self.global_task_queue: List[AgentTask] = []
        
        # Herramientas específicas del coordinador
        self.tools = {
            "assign_task": self._assign_task,
            "coordinate_agents": self._coordinate_agents,
            "manage_workflow": self._manage_workflow,
            "resolve_conflicts": self._resolve_conflicts,
            "monitor_progress": self._monitor_progress,
            "synthesize_results": self._synthesize_results
        }
        
        self.logger.info("Agente Coordinador inicializado")
    
    def initialize(self) -> bool:
        """Inicializar el agente"""
        try:
            # Configurar LLM
            self.llm = ChatOpenAI(
                model=self.config.ai.model,
                temperature=self.config.ai.temperature,
                openai_api_key=self.config.ai.openai_api_key
            )
            
            # Configurar herramientas de LangChain
            langchain_tools = self._create_langchain_tools()
            
            # Crear prompt template
            prompt = self._create_prompt_template()
            
            # Crear agente ReAct
            agent = create_react_agent(
                llm=self.llm,
                tools=langchain_tools,
                prompt=prompt
            )
            
            # Crear ejecutor del agente
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=langchain_tools,
                verbose=True,
                max_iterations=5,
                early_stopping_method="generate"
            )
            
            self.logger.info("Agente Coordinador configurado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al inicializar Agente Coordinador: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Obtener capacidades del agente"""
        return [
            "Coordinar colaboración entre agentes",
            "Asignar tareas a agentes especializados",
            "Gestionar flujos de trabajo complejos",
            "Resolver conflictos entre agentes",
            "Monitorear progreso de tareas",
            "Sintetizar resultados de múltiples agentes",
            "Optimizar distribución de carga de trabajo",
            "Mantener contexto compartido entre agentes"
        ]
    
    def register_agent(self, agent_name: str, agent_instance: Any) -> bool:
        """Registrar un agente en el sistema"""
        try:
            self.available_agents[agent_name] = agent_instance
            self.agent_status[agent_name] = "idle"
            
            self.logger.info(f"Agente registrado: {agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al registrar agente {agent_name}: {e}")
            return False
    
    def unregister_agent(self, agent_name: str) -> bool:
        """Desregistrar un agente del sistema"""
        try:
            if agent_name in self.available_agents:
                del self.available_agents[agent_name]
                del self.agent_status[agent_name]
                
                self.logger.info(f"Agente desregistrado: {agent_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error al desregistrar agente {agent_name}: {e}")
            return False
    
    def process_task(self, task: AgentTask) -> Any:
        """Procesar tarea de coordinación"""
        try:
            self.logger.info(f"Procesando tarea de coordinación: {task.task_id}")
            self.set_status(self.status.THINKING)
            
            # Ejecutar coordinación usando LangChain
            result = self.agent_executor.invoke({
                "input": task.description,
                "chat_history": self.conversation_memory.get_conversation_history()
            })
            
            # Guardar resultado en memoria
            self._save_coordination_result(task.task_id, result)
            
            # Actualizar métricas
            self.tasks_completed += 1
            
            self.logger.info(f"Tarea de coordinación completada: {task.task_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al procesar tarea {task.task_id}: {e}")
            self.tasks_failed += 1
            raise
    
    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar contexto específico del agente"""
        try:
            analysis = {
                "context_type": "multi_agent_coordination",
                "coordination_type": context.get("coordination_type", "workflow"),
                "available_agents": list(self.available_agents.keys()),
                "agent_status": self.agent_status.copy(),
                "task_requirements": context.get("task_requirements", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            # Buscar en memoria vectorial para coordinaciones similares
            similar_coordinations = self.vector_memory.search(
                f"coordination {context.get('coordination_type', 'workflow')}", 
                limit=3
            )
            analysis["similar_coordinations"] = [
                {
                    "content": result.entry.content,
                    "similarity": result.similarity,
                    "metadata": result.entry.metadata
                }
                for result in similar_coordinations
            ]
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error al analizar contexto: {e}")
            return {"error": str(e)}
    
    def _identify_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identificar acciones necesarias para coordinación"""
        try:
            actions = []
            
            coordination_type = analysis.get("coordination_type", "workflow")
            task_requirements = analysis.get("task_requirements", {})
            available_agents = analysis.get("available_agents", [])
            
            # Acciones básicas de coordinación
            if coordination_type in ["workflow", "full"]:
                actions.append({
                    "action": "manage_workflow",
                    "priority": 1,
                    "parameters": {
                        "task_requirements": task_requirements,
                        "available_agents": available_agents
                    }
                })
            
            if coordination_type in ["assignment", "full"]:
                actions.append({
                    "action": "assign_task",
                    "priority": 2,
                    "parameters": {
                        "task_requirements": task_requirements,
                        "available_agents": available_agents
                    }
                })
            
            if coordination_type in ["coordination", "full"]:
                actions.append({
                    "action": "coordinate_agents",
                    "priority": 3,
                    "parameters": {
                        "available_agents": available_agents
                    }
                })
            
            if coordination_type in ["monitoring", "full"]:
                actions.append({
                    "action": "monitor_progress",
                    "priority": 4,
                    "parameters": {
                        "available_agents": available_agents
                    }
                })
            
            if coordination_type in ["synthesis", "full"]:
                actions.append({
                    "action": "synthesize_results",
                    "priority": 5,
                    "parameters": {
                        "available_agents": available_agents
                    }
                })
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Error al identificar acciones: {e}")
            return [{"action": "error", "priority": 1, "message": str(e)}]
    
    def _execute_action(self, action: Dict[str, Any]) -> Any:
        """Ejecutar acción específica de coordinación"""
        try:
            action_name = action["action"]
            parameters = action.get("parameters", {})
            
            self.logger.info(f"Ejecutando acción: {action_name}")
            
            if action_name == "assign_task":
                return self._assign_task(**parameters)
            elif action_name == "coordinate_agents":
                return self._coordinate_agents(**parameters)
            elif action_name == "manage_workflow":
                return self._manage_workflow(**parameters)
            elif action_name == "resolve_conflicts":
                return self._resolve_conflicts(**parameters)
            elif action_name == "monitor_progress":
                return self._monitor_progress(**parameters)
            elif action_name == "synthesize_results":
                return self._synthesize_results(**parameters)
            else:
                raise ValueError(f"Acción no reconocida: {action_name}")
                
        except Exception as e:
            self.logger.error(f"Error al ejecutar acción {action['action']}: {e}")
            raise
    
    def _create_langchain_tools(self) -> List[Tool]:
        """Crear herramientas de LangChain"""
        tools = []
        
        for tool_name, tool_func in self.tools.items():
            tool = Tool(
                name=tool_name,
                description=self._get_tool_description(tool_name),
                func=tool_func
            )
            tools.append(tool)
        
        return tools
    
    def _get_tool_description(self, tool_name: str) -> str:
        """Obtener descripción de herramienta"""
        descriptions = {
            "assign_task": "Asigna tareas específicas a agentes especializados basándose en sus capacidades",
            "coordinate_agents": "Coordina la colaboración entre múltiples agentes para tareas complejas",
            "manage_workflow": "Gestiona flujos de trabajo complejos que requieren múltiples agentes",
            "resolve_conflicts": "Resuelve conflictos entre agentes y toma decisiones de coordinación",
            "monitor_progress": "Monitorea el progreso de tareas asignadas a diferentes agentes",
            "synthesize_results": "Sintetiza resultados de múltiples agentes en un resultado coherente"
        }
        return descriptions.get(tool_name, f"Herramienta: {tool_name}")
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Crear template de prompt para el agente"""
        template = """
Eres un agente coordinador especializado en gestionar la colaboración entre múltiples agentes para la generación de pruebas unitarias .NET. Tu tarea es coordinar, asignar tareas y sintetizar resultados.

Tienes acceso a las siguientes herramientas:
{tools}

Agentes disponibles: {available_agents}

Usa el siguiente formato:

Question: la pregunta de entrada que debes responder
Thought: siempre debes pensar en qué hacer
Action: la acción a tomar, debe ser una de [{tool_names}]
Action Input: la entrada para la acción
Observation: el resultado de la acción
... (este Thought/Action/Action Input/Observation puede repetirse N veces)
Thought: ahora sé la respuesta final
Final Answer: la respuesta final a la pregunta original

Historial de conversación:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}
"""
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names", "chat_history", "available_agents"]
        )
    
    # Métodos de herramientas específicas
    def _assign_task(self, task_requirements: Dict[str, Any], available_agents: List[str]) -> Dict[str, Any]:
        """Asignar tarea a agente específico"""
        try:
            # Determinar el agente más apropiado usando LLM
            prompt = f"""
Analiza los siguientes requisitos de tarea y determina qué agente es más apropiado:

Requisitos de tarea: {task_requirements}
Agentes disponibles: {available_agents}

Capacidades de cada agente:
- analysis_agent: Análisis de código .NET, extracción de información
- generation_agent: Generación de código de pruebas, templates
- validation_agent: Validación de código, ejecución de pruebas
- optimization_agent: Optimización de rendimiento, refactoring

Determina:
1. Qué agente es más apropiado
2. Qué subtareas se pueden asignar
3. Qué información necesita el agente
4. Qué dependencias existen

Responde en formato JSON.
"""
            
            response = self.llm.invoke(prompt)
            assignment_analysis = response.content
            
            # Procesar asignación
            selected_agent = self._select_best_agent(task_requirements, available_agents)
            
            if selected_agent and selected_agent in self.available_agents:
                # Crear tarea para el agente
                task = AgentTask(
                    task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    description=str(task_requirements),
                    priority=1,
                    status="assigned"
                )
                
                # Asignar tarea al agente
                agent = self.available_agents[selected_agent]
                success = agent.add_task(task)
                
                if success:
                    self.agent_status[selected_agent] = "busy"
                    
                    return {
                        "success": True,
                        "assigned_agent": selected_agent,
                        "task_id": task.task_id,
                        "assignment_analysis": assignment_analysis
                    }
            
            return {
                "success": False,
                "error": "No se pudo asignar la tarea a ningún agente"
            }
            
        except Exception as e:
            self.logger.error(f"Error al asignar tarea: {e}")
            return {"success": False, "error": str(e)}
    
    def _coordinate_agents(self, available_agents: List[str]) -> Dict[str, Any]:
        """Coordinar colaboración entre agentes"""
        try:
            # Analizar colaboración necesaria usando LLM
            prompt = f"""
Analiza qué tipo de colaboración es necesaria entre los siguientes agentes:

Agentes disponibles: {available_agents}

Determina:
1. Qué agentes pueden colaborar
2. Qué flujo de trabajo es más eficiente
3. Qué información debe compartirse
4. Qué dependencias existen entre agentes

Proporciona un plan de colaboración detallado.
"""
            
            response = self.llm.invoke(prompt)
            coordination_plan = response.content
            
            # Implementar plan de coordinación
            coordination_result = self._implement_coordination_plan(coordination_plan, available_agents)
            
            return {
                "success": True,
                "coordination_plan": coordination_plan,
                "coordination_result": coordination_result
            }
            
        except Exception as e:
            self.logger.error(f"Error al coordinar agentes: {e}")
            return {"success": False, "error": str(e)}
    
    def _manage_workflow(self, task_requirements: Dict[str, Any], available_agents: List[str]) -> Dict[str, Any]:
        """Gestionar flujo de trabajo complejo"""
        try:
            # Crear flujo de trabajo usando LLM
            prompt = f"""
Crea un flujo de trabajo para los siguientes requisitos:

Requisitos: {task_requirements}
Agentes disponibles: {available_agents}

El flujo debe incluir:
1. Secuencia de tareas
2. Dependencias entre tareas
3. Asignación de agentes
4. Puntos de sincronización
5. Manejo de errores

Proporciona un flujo de trabajo detallado.
"""
            
            response = self.llm.invoke(prompt)
            workflow_plan = response.content
            
            # Implementar flujo de trabajo
            workflow_result = self._implement_workflow(workflow_plan, task_requirements, available_agents)
            
            return {
                "success": True,
                "workflow_plan": workflow_plan,
                "workflow_result": workflow_result
            }
            
        except Exception as e:
            self.logger.error(f"Error al gestionar flujo de trabajo: {e}")
            return {"success": False, "error": str(e)}
    
    def _resolve_conflicts(self, conflict_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resolver conflictos entre agentes"""
        try:
            # Analizar conflictos usando LLM
            prompt = f"""
Analiza y resuelve los siguientes conflictos entre agentes:

Datos de conflicto: {conflict_data or 'No hay conflictos específicos'}

Determina:
1. Naturaleza del conflicto
2. Agentes involucrados
3. Soluciones posibles
4. Mejor estrategia de resolución

Proporciona una resolución detallada.
"""
            
            response = self.llm.invoke(prompt)
            conflict_resolution = response.content
            
            return {
                "success": True,
                "conflict_resolution": conflict_resolution
            }
            
        except Exception as e:
            self.logger.error(f"Error al resolver conflictos: {e}")
            return {"success": False, "error": str(e)}
    
    def _monitor_progress(self, available_agents: List[str]) -> Dict[str, Any]:
        """Monitorear progreso de agentes"""
        try:
            progress_report = {}
            
            for agent_name in available_agents:
                if agent_name in self.available_agents:
                    agent = self.available_agents[agent_name]
                    metrics = agent.get_metrics()
                    
                    progress_report[agent_name] = {
                        "status": self.agent_status.get(agent_name, "unknown"),
                        "tasks_completed": metrics.get("tasks_completed", 0),
                        "tasks_failed": metrics.get("tasks_failed", 0),
                        "queue_size": metrics.get("queue_size", 0),
                        "processing_time": metrics.get("total_processing_time", 0)
                    }
            
            return {
                "success": True,
                "progress_report": progress_report,
                "overall_status": self._calculate_overall_status(progress_report)
            }
            
        except Exception as e:
            self.logger.error(f"Error al monitorear progreso: {e}")
            return {"success": False, "error": str(e)}
    
    def _synthesize_results(self, available_agents: List[str]) -> Dict[str, Any]:
        """Sintetizar resultados de múltiples agentes"""
        try:
            # Recopilar resultados de agentes
            agent_results = {}
            
            for agent_name in available_agents:
                if agent_name in self.available_agents:
                    agent = self.available_agents[agent_name]
                    # Obtener resultados recientes del agente
                    recent_results = self._get_recent_agent_results(agent_name)
                    agent_results[agent_name] = recent_results
            
            # Sintetizar resultados usando LLM
            prompt = f"""
Sintetiza los siguientes resultados de múltiples agentes:

Resultados por agente: {agent_results}

Crea una síntesis coherente que incluya:
1. Resumen de resultados principales
2. Patrones identificados
3. Recomendaciones consolidadas
4. Próximos pasos sugeridos
5. Conclusiones generales

Proporciona una síntesis clara y accionable.
"""
            
            response = self.llm.invoke(prompt)
            synthesis = response.content
            
            return {
                "success": True,
                "agent_results": agent_results,
                "synthesis": synthesis
            }
            
        except Exception as e:
            self.logger.error(f"Error al sintetizar resultados: {e}")
            return {"success": False, "error": str(e)}
    
    # Métodos auxiliares
    def _select_best_agent(self, task_requirements: Dict[str, Any], available_agents: List[str]) -> Optional[str]:
        """Seleccionar el mejor agente para una tarea"""
        # Lógica básica de selección
        task_type = task_requirements.get("type", "unknown")
        
        if "analysis" in task_type.lower():
            return "analysis_agent" if "analysis_agent" in available_agents else None
        elif "generation" in task_type.lower():
            return "generation_agent" if "generation_agent" in available_agents else None
        elif "validation" in task_type.lower():
            return "validation_agent" if "validation_agent" in available_agents else None
        elif "optimization" in task_type.lower():
            return "optimization_agent" if "optimization_agent" in available_agents else None
        
        # Por defecto, usar el primer agente disponible
        return available_agents[0] if available_agents else None
    
    def _implement_coordination_plan(self, plan: str, available_agents: List[str]) -> Dict[str, Any]:
        """Implementar plan de coordinación"""
        # Implementación básica
        return {"plan_implemented": True, "agents_coordinated": available_agents}
    
    def _implement_workflow(self, plan: str, requirements: Dict[str, Any], available_agents: List[str]) -> Dict[str, Any]:
        """Implementar flujo de trabajo"""
        # Implementación básica
        return {"workflow_implemented": True, "steps_completed": 0}
    
    def _calculate_overall_status(self, progress_report: Dict[str, Any]) -> str:
        """Calcular estado general del sistema"""
        total_tasks = sum(agent.get("tasks_completed", 0) + agent.get("tasks_failed", 0) 
                         for agent in progress_report.values())
        
        if total_tasks == 0:
            return "idle"
        elif all(agent.get("status") == "idle" for agent in progress_report.values()):
            return "completed"
        else:
            return "busy"
    
    def _get_recent_agent_results(self, agent_name: str) -> Dict[str, Any]:
        """Obtener resultados recientes de un agente"""
        # Implementación básica
        return {"recent_results": "No hay resultados recientes"}
    
    def _save_coordination_result(self, task_id: str, result: Any):
        """Guardar resultado de coordinación en memoria"""
        try:
            self.vector_memory.add_entry(
                content=f"Resultado de coordinación para tarea {task_id}",
                metadata={
                    "task_id": task_id,
                    "result_type": type(result).__name__,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error al guardar resultado de coordinación: {e}")


# Instancia global del agente coordinador
coordinator_agent = CoordinatorAgent()
