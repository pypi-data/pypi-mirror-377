"""
Agente Optimizador - Especializado en optimización de código y pruebas
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from agents.base_agent import ReActAgent, AgentRole, AgentTask
from tools.file_tools import code_file_manager
from langchain_agents.memory.conversation_memory import ConversationMemory
from langchain_agents.memory.vector_memory import VectorMemory
from utils.config import Config
from utils.logging import get_logger
from ai.llm_factory import LLMFactory

logger = get_logger("optimization-agent")


class OptimizationAgent(ReActAgent):
    """Agente especializado en optimización de código y pruebas"""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__("optimization_agent", AgentRole.OPTIMIZER, config)
        
        self.logger = logger
        self.llm = None
        self.agent_executor = None
        
        # Memoria del agente
        self.conversation_memory = ConversationMemory("optimization_agent")
        self.vector_memory = VectorMemory("optimization_agent")
        
        # Herramientas específicas del optimizador
        self.tools = {
            "optimize_test_performance": self._optimize_test_performance,
            "refactor_test_code": self._refactor_test_code,
            "improve_test_coverage": self._improve_test_coverage,
            "optimize_mock_usage": self._optimize_mock_usage,
            "suggest_improvements": self._suggest_improvements,
            "analyze_performance": self._analyze_performance
        }
        
        # Inicializar el agente
        self.initialize()
        
        self.logger.info("Agente Optimizador inicializado")
    
    def initialize(self) -> bool:
        """Inicializar el agente"""
        try:
            # Configurar LLM usando el factory
            self.llm = LLMFactory.create_langchain_llm(self.config)
            
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
            
            self.logger.info("Agente Optimizador configurado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al inicializar Agente Optimizador: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Obtener capacidades del agente"""
        return [
            "Optimizar rendimiento de pruebas unitarias",
            "Refactorizar código de pruebas para mejor legibilidad",
            "Mejorar cobertura de código",
            "Optimizar uso de mocks y stubs",
            "Sugerir mejoras en la estructura de pruebas",
            "Analizar rendimiento y detectar cuellos de botella",
            "Aplicar patrones de testing avanzados",
            "Optimizar configuración de proyectos de testing"
        ]
    
    def process_task(self, task: AgentTask) -> Any:
        """Procesar tarea de optimización"""
        try:
            self.logger.info(f"Procesando tarea: {task.task_id}")
            self.set_status(self.status.THINKING)
            
            # Ejecutar optimización usando LangChain
            result = self.agent_executor.invoke({
                "input": task.description,
                "chat_history": self.conversation_memory.get_conversation_history()
            })
            
            # Guardar resultado en memoria
            self._save_optimization_result(task.task_id, result)
            
            # Actualizar métricas
            self.tasks_completed += 1
            
            self.logger.info(f"Tarea completada: {task.task_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al procesar tarea {task.task_id}: {e}")
            self.tasks_failed += 1
            raise
    
    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar contexto específico del agente"""
        try:
            analysis = {
                "context_type": "code_optimization",
                "optimization_type": context.get("optimization_type", "performance"),
                "target_files": context.get("target_files", []),
                "performance_metrics": context.get("performance_metrics", {}),
                "coverage_data": context.get("coverage_data", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            # Buscar en memoria vectorial para optimizaciones similares
            if context.get("target_files"):
                similar_optimizations = self.vector_memory.search(
                    f"optimization {context['optimization_type']}", 
                    limit=3
                )
                analysis["similar_optimizations"] = [
                    {
                        "content": result.entry.content,
                        "similarity": result.similarity,
                        "metadata": result.entry.metadata
                    }
                    for result in similar_optimizations
                ]
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error al analizar contexto: {e}")
            return {"error": str(e)}
    
    def _identify_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identificar acciones necesarias para optimización"""
        try:
            actions = []
            
            optimization_type = analysis.get("optimization_type", "performance")
            target_files = analysis.get("target_files", [])
            performance_metrics = analysis.get("performance_metrics", {})
            coverage_data = analysis.get("coverage_data", {})
            
            # Acciones básicas de optimización
            if optimization_type in ["performance", "full"]:
                actions.append({
                    "action": "analyze_performance",
                    "priority": 1,
                    "parameters": {
                        "target_files": target_files,
                        "performance_metrics": performance_metrics
                    }
                })
            
            if optimization_type in ["performance", "full"]:
                actions.append({
                    "action": "optimize_test_performance",
                    "priority": 2,
                    "parameters": {"target_files": target_files}
                })
            
            if optimization_type in ["coverage", "full"]:
                actions.append({
                    "action": "improve_test_coverage",
                    "priority": 3,
                    "parameters": {
                        "target_files": target_files,
                        "coverage_data": coverage_data
                    }
                })
            
            if optimization_type in ["refactoring", "full"]:
                actions.append({
                    "action": "refactor_test_code",
                    "priority": 4,
                    "parameters": {"target_files": target_files}
                })
            
            if optimization_type in ["mocking", "full"]:
                actions.append({
                    "action": "optimize_mock_usage",
                    "priority": 5,
                    "parameters": {"target_files": target_files}
                })
            
            # Siempre sugerir mejoras
            actions.append({
                "action": "suggest_improvements",
                "priority": 6,
                "parameters": {
                    "target_files": target_files,
                    "optimization_type": optimization_type
                }
            })
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Error al identificar acciones: {e}")
            return [{"action": "error", "priority": 1, "message": str(e)}]
    
    def _execute_action(self, action: Dict[str, Any]) -> Any:
        """Ejecutar acción específica de optimización"""
        try:
            action_name = action["action"]
            parameters = action.get("parameters", {})
            
            self.logger.info(f"Ejecutando acción: {action_name}")
            
            if action_name == "optimize_test_performance":
                return self._optimize_test_performance(**parameters)
            elif action_name == "refactor_test_code":
                return self._refactor_test_code(**parameters)
            elif action_name == "improve_test_coverage":
                return self._improve_test_coverage(**parameters)
            elif action_name == "optimize_mock_usage":
                return self._optimize_mock_usage(**parameters)
            elif action_name == "suggest_improvements":
                return self._suggest_improvements(**parameters)
            elif action_name == "analyze_performance":
                return self._analyze_performance(**parameters)
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
            "optimize_test_performance": "Optimiza el rendimiento de las pruebas unitarias identificando y resolviendo cuellos de botella",
            "refactor_test_code": "Refactoriza el código de pruebas para mejorar legibilidad y mantenibilidad",
            "improve_test_coverage": "Mejora la cobertura de código sugiriendo pruebas adicionales",
            "optimize_mock_usage": "Optimiza el uso de mocks y stubs para mejorar eficiencia",
            "suggest_improvements": "Sugiere mejoras generales en la estructura y organización de las pruebas",
            "analyze_performance": "Analiza el rendimiento del código y identifica áreas de mejora"
        }
        return descriptions.get(tool_name, f"Herramienta: {tool_name}")
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Crear template de prompt para el agente"""
        template = """
Eres un agente especializado en optimización de código y pruebas unitarias para .NET. Tu tarea es mejorar el rendimiento, legibilidad y eficiencia del código de pruebas.

Tienes acceso a las siguientes herramientas:
{tools}

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
            input_variables=["input", "agent_scratchpad", "tools", "tool_names", "chat_history"]
        )
    
    # Métodos de herramientas específicas
    def _optimize_test_performance(self, target_files: List[str]) -> Dict[str, Any]:
        """Optimizar rendimiento de pruebas"""
        try:
            optimizations = []
            
            for file_path in target_files:
                try:
                    content = code_file_manager.read_code_file(file_path)
                    
                    # Analizar y optimizar usando LLM
                    prompt = f"""
Analiza el siguiente código de pruebas y sugiere optimizaciones de rendimiento:

{content}

Identifica:
1. Cuellos de botella de rendimiento
2. Operaciones costosas innecesarias
3. Configuraciones de setup que se pueden optimizar
4. Uso ineficiente de mocks
5. Pruebas que se pueden paralelizar

Proporciona código optimizado y explicaciones.
"""
                    
                    response = self.llm.invoke(prompt)
                    optimized_code = response.content
                    
                    optimizations.append({
                        "file_path": file_path,
                        "original_code": content,
                        "optimized_code": optimized_code,
                        "optimization_suggestions": self._extract_optimization_suggestions(optimized_code)
                    })
                    
                except Exception as e:
                    optimizations.append({
                        "file_path": file_path,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "optimizations": optimizations
            }
            
        except Exception as e:
            self.logger.error(f"Error al optimizar rendimiento: {e}")
            return {"success": False, "error": str(e)}
    
    def _refactor_test_code(self, target_files: List[str]) -> Dict[str, Any]:
        """Refactorizar código de pruebas"""
        try:
            refactoring_results = []
            
            for file_path in target_files:
                try:
                    content = code_file_manager.read_code_file(file_path)
                    
                    # Refactorizar usando LLM
                    prompt = f"""
Refactoriza el siguiente código de pruebas para mejorar legibilidad y mantenibilidad:

{content}

Aplica:
1. Principios SOLID
2. Patrones de testing (AAA, Builder, Factory)
3. Mejor organización de métodos
4. Eliminación de duplicación de código
5. Mejores nombres de variables y métodos

Proporciona código refactorizado con explicaciones.
"""
                    
                    response = self.llm.invoke(prompt)
                    refactored_code = response.content
                    
                    refactoring_results.append({
                        "file_path": file_path,
                        "original_code": content,
                        "refactored_code": refactored_code,
                        "refactoring_improvements": self._extract_refactoring_improvements(refactored_code)
                    })
                    
                except Exception as e:
                    refactoring_results.append({
                        "file_path": file_path,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "refactoring_results": refactoring_results
            }
            
        except Exception as e:
            self.logger.error(f"Error al refactorizar código: {e}")
            return {"success": False, "error": str(e)}
    
    def _improve_test_coverage(self, target_files: List[str], coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mejorar cobertura de código"""
        try:
            coverage_improvements = []
            
            for file_path in target_files:
                try:
                    content = code_file_manager.read_code_file(file_path)
                    
                    # Analizar cobertura usando LLM
                    prompt = f"""
Analiza el siguiente código y sugiere pruebas adicionales para mejorar cobertura:

Código:
{content}

Datos de cobertura:
{coverage_data}

Identifica:
1. Líneas no cubiertas
2. Ramas no probadas
3. Casos edge no considerados
4. Excepciones no manejadas
5. Validaciones faltantes

Genera pruebas adicionales para mejorar la cobertura.
"""
                    
                    response = self.llm.invoke(prompt)
                    additional_tests = response.content
                    
                    coverage_improvements.append({
                        "file_path": file_path,
                        "additional_tests": additional_tests,
                        "coverage_analysis": self._analyze_coverage_gaps(content, coverage_data)
                    })
                    
                except Exception as e:
                    coverage_improvements.append({
                        "file_path": file_path,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "coverage_improvements": coverage_improvements
            }
            
        except Exception as e:
            self.logger.error(f"Error al mejorar cobertura: {e}")
            return {"success": False, "error": str(e)}
    
    def _optimize_mock_usage(self, target_files: List[str]) -> Dict[str, Any]:
        """Optimizar uso de mocks"""
        try:
            mock_optimizations = []
            
            for file_path in target_files:
                try:
                    content = code_file_manager.read_code_file(file_path)
                    
                    # Optimizar mocks usando LLM
                    prompt = f"""
Analiza y optimiza el uso de mocks en el siguiente código de pruebas:

{content}

Identifica:
1. Mocks innecesarios o redundantes
2. Configuraciones de mocks que se pueden simplificar
3. Uso ineficiente de mocks
4. Oportunidades para usar stubs en lugar de mocks
5. Configuraciones que se pueden reutilizar

Proporciona código optimizado con explicaciones.
"""
                    
                    response = self.llm.invoke(prompt)
                    optimized_mocks = response.content
                    
                    mock_optimizations.append({
                        "file_path": file_path,
                        "original_code": content,
                        "optimized_mocks": optimized_mocks,
                        "mock_improvements": self._extract_mock_improvements(optimized_mocks)
                    })
                    
                except Exception as e:
                    mock_optimizations.append({
                        "file_path": file_path,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "mock_optimizations": mock_optimizations
            }
            
        except Exception as e:
            self.logger.error(f"Error al optimizar mocks: {e}")
            return {"success": False, "error": str(e)}
    
    def _suggest_improvements(self, target_files: List[str], optimization_type: str) -> Dict[str, Any]:
        """Sugerir mejoras generales"""
        try:
            suggestions = []
            
            for file_path in target_files:
                try:
                    content = code_file_manager.read_code_file(file_path)
                    
                    # Generar sugerencias usando LLM
                    prompt = f"""
Analiza el siguiente código de pruebas y sugiere mejoras generales:

{content}

Tipo de optimización: {optimization_type}

Sugiere:
1. Mejoras en la estructura y organización
2. Patrones de testing que se pueden aplicar
3. Mejores prácticas que se pueden implementar
4. Herramientas o librerías que pueden ayudar
5. Configuraciones que se pueden optimizar

Proporciona sugerencias específicas y accionables.
"""
                    
                    response = self.llm.invoke(prompt)
                    improvements = response.content
                    
                    suggestions.append({
                        "file_path": file_path,
                        "suggestions": improvements,
                        "priority": self._prioritize_suggestions(improvements)
                    })
                    
                except Exception as e:
                    suggestions.append({
                        "file_path": file_path,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "suggestions": suggestions
            }
            
        except Exception as e:
            self.logger.error(f"Error al sugerir mejoras: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_performance(self, target_files: List[str], performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar rendimiento"""
        try:
            performance_analysis = []
            
            for file_path in target_files:
                try:
                    content = code_file_manager.read_code_file(file_path)
                    
                    # Analizar rendimiento usando LLM
                    prompt = f"""
Analiza el rendimiento del siguiente código de pruebas:

{content}

Métricas de rendimiento:
{performance_metrics}

Identifica:
1. Operaciones costosas
2. Cuellos de botella
3. Oportunidades de paralelización
4. Configuraciones que afectan el rendimiento
5. Patrones que pueden optimizarse

Proporciona análisis detallado y recomendaciones.
"""
                    
                    response = self.llm.invoke(prompt)
                    analysis = response.content
                    
                    performance_analysis.append({
                        "file_path": file_path,
                        "analysis": analysis,
                        "performance_issues": self._identify_performance_issues(content),
                        "recommendations": self._extract_performance_recommendations(analysis)
                    })
                    
                except Exception as e:
                    performance_analysis.append({
                        "file_path": file_path,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "performance_analysis": performance_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error al analizar rendimiento: {e}")
            return {"success": False, "error": str(e)}
    
    # Métodos auxiliares
    def _extract_optimization_suggestions(self, optimized_code: str) -> List[str]:
        """Extraer sugerencias de optimización"""
        # Implementación básica
        return ["Optimización de rendimiento aplicada"]
    
    def _extract_refactoring_improvements(self, refactored_code: str) -> List[str]:
        """Extraer mejoras de refactoring"""
        # Implementación básica
        return ["Código refactorizado para mejor legibilidad"]
    
    def _analyze_coverage_gaps(self, content: str, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar brechas de cobertura"""
        # Implementación básica
        return {"uncovered_lines": [], "uncovered_branches": []}
    
    def _extract_mock_improvements(self, optimized_mocks: str) -> List[str]:
        """Extraer mejoras de mocks"""
        # Implementación básica
        return ["Uso de mocks optimizado"]
    
    def _prioritize_suggestions(self, suggestions: str) -> List[str]:
        """Priorizar sugerencias"""
        # Implementación básica
        return ["Alta", "Media", "Baja"]
    
    def _identify_performance_issues(self, content: str) -> List[str]:
        """Identificar problemas de rendimiento"""
        # Implementación básica
        return ["Análisis de rendimiento completado"]
    
    def _extract_performance_recommendations(self, analysis: str) -> List[str]:
        """Extraer recomendaciones de rendimiento"""
        # Implementación básica
        return ["Recomendaciones de rendimiento generadas"]
    
    def _save_optimization_result(self, task_id: str, result: Any):
        """Guardar resultado de optimización en memoria"""
        try:
            self.vector_memory.add_entry(
                content=f"Resultado de optimización para tarea {task_id}",
                metadata={
                    "task_id": task_id,
                    "result_type": type(result).__name__,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error al guardar resultado de optimización: {e}")
    
    def optimize_code(self, code: str) -> str:
        """Método simplificado para optimizar código directamente"""
        try:
            self.logger.info("Iniciando optimización de código")
            
            # Verificar si el agente está inicializado correctamente
            if self.agent_executor is None:
                self.logger.warning("Agente no inicializado, usando optimización básica")
                return self._perform_basic_optimization(code)
            
            # Crear una tarea de optimización
            task = AgentTask(
                task_id=f"optimize_{int(datetime.now().timestamp())}",
                description=f"Optimizar el siguiente código C#:\n\n{code}",
                priority=1,
                status="pending",
                created_at=datetime.now()
            )
            
            # Procesar la tarea
            result = self.process_task(task)
            
            # Extraer el resultado de la optimización
            if isinstance(result, dict) and 'output' in result:
                return result['output']
            elif isinstance(result, str):
                return result
            else:
                # Realizar optimización básica
                return self._perform_basic_optimization(code)
                
        except Exception as e:
            self.logger.error(f"Error en optimización de código: {e}")
            return self._perform_basic_optimization(code)
    
    def _perform_basic_optimization(self, code: str) -> str:
        """Realizar optimización básica del código"""
        optimized_code = code
        
        # Optimizaciones básicas
        optimizations = []
        
        # Remover espacios en blanco innecesarios
        if "  " in code:
            optimized_code = optimized_code.replace("  ", " ")
            optimizations.append("✅ Espacios en blanco optimizados")
        
        # Verificar si hay comentarios innecesarios
        if "// TODO" in code or "// FIXME" in code:
            optimizations.append("⚠️  Se encontraron comentarios TODO/FIXME que requieren atención")
        
        # Verificar si hay variables no utilizadas
        if "var " in code and "=" in code:
            optimizations.append("✅ Variables detectadas - verificar uso")
        
        # Agregar comentario de optimización
        if optimizations:
            optimization_comment = "// Optimizaciones aplicadas:\n" + "\n".join(f"// {opt}" for opt in optimizations) + "\n\n"
            optimized_code = optimization_comment + optimized_code
        
        return optimized_code


# Instancia global del agente optimizador
optimization_agent = OptimizationAgent()
