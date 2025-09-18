"""
Agente Validador - Especializado en validación de código y pruebas
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from agents.base_agent import ReActAgent, AgentRole, AgentTask
from tools.dotnet_tools import command_executor
from tools.file_tools import code_file_manager
from langchain_agents.memory.conversation_memory import ConversationMemory
from langchain_agents.memory.vector_memory import VectorMemory
from utils.config import Config
from utils.logging import get_logger
from ai.llm_factory import LLMFactory

logger = get_logger("validation-agent")


class ValidationAgent(ReActAgent):
    """Agente especializado en validación de código y pruebas"""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__("validation_agent", AgentRole.VALIDATOR, config)
        
        self.logger = logger
        self.llm = None
        self.agent_executor = None
        
        # Memoria del agente
        self.conversation_memory = ConversationMemory("validation_agent")
        self.vector_memory = VectorMemory("validation_agent")
        
        # Herramientas específicas del validador
        self.tools = {
            "validate_code_syntax": self._validate_code_syntax,
            "run_tests": self._run_tests,
            "check_code_coverage": self._check_code_coverage,
            "validate_test_structure": self._validate_test_structure,
            "check_best_practices": self._check_best_practices,
            "compile_project": self._compile_project
        }
        
        # Inicializar el agente
        self.initialize()
        
        self.logger.info("Agente Validador inicializado")
    
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
            
            self.logger.info("Agente Validador configurado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al inicializar Agente Validador: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Obtener capacidades del agente"""
        return [
            "Validar sintaxis de código C#",
            "Ejecutar pruebas unitarias",
            "Verificar cobertura de código",
            "Validar estructura de pruebas",
            "Verificar mejores prácticas de testing",
            "Compilar proyectos .NET",
            "Detectar errores de compilación",
            "Validar configuración de proyectos"
        ]
    
    def process_task(self, task: AgentTask) -> Any:
        """Procesar tarea de validación"""
        try:
            self.logger.info(f"Procesando tarea: {task.task_id}")
            self.set_status(self.status.THINKING)
            
            # Ejecutar validación usando LangChain
            result = self.agent_executor.invoke({
                "input": task.description,
                "chat_history": self.conversation_memory.get_conversation_history()
            })
            
            # Guardar resultado en memoria
            self._save_validation_result(task.task_id, result)
            
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
                "context_type": "code_validation",
                "validation_type": context.get("validation_type", "full"),
                "target_files": context.get("target_files", []),
                "project_path": context.get("project_path"),
                "validation_rules": context.get("validation_rules", []),
                "timestamp": datetime.now().isoformat()
            }
            
            # Buscar en memoria vectorial para validaciones similares
            if context.get("project_path"):
                similar_validations = self.vector_memory.search(
                    f"validation {context['project_path']}", 
                    limit=3
                )
                analysis["similar_validations"] = [
                    {
                        "content": result.entry.content,
                        "similarity": result.similarity,
                        "metadata": result.entry.metadata
                    }
                    for result in similar_validations
                ]
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error al analizar contexto: {e}")
            return {"error": str(e)}
    
    def _identify_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identificar acciones necesarias para validación"""
        try:
            actions = []
            
            validation_type = analysis.get("validation_type", "full")
            target_files = analysis.get("target_files", [])
            project_path = analysis.get("project_path")
            
            # Acciones básicas de validación
            if validation_type in ["full", "syntax"]:
                actions.append({
                    "action": "validate_code_syntax",
                    "priority": 1,
                    "parameters": {"target_files": target_files}
                })
            
            if validation_type in ["full", "compilation"]:
                actions.append({
                    "action": "compile_project",
                    "priority": 2,
                    "parameters": {"project_path": project_path}
                })
            
            if validation_type in ["full", "tests"]:
                actions.append({
                    "action": "run_tests",
                    "priority": 3,
                    "parameters": {"project_path": project_path}
                })
            
            if validation_type in ["full", "coverage"]:
                actions.append({
                    "action": "check_code_coverage",
                    "priority": 4,
                    "parameters": {"project_path": project_path}
                })
            
            if validation_type in ["full", "structure"]:
                actions.append({
                    "action": "validate_test_structure",
                    "priority": 5,
                    "parameters": {"target_files": target_files}
                })
            
            if validation_type in ["full", "practices"]:
                actions.append({
                    "action": "check_best_practices",
                    "priority": 6,
                    "parameters": {"target_files": target_files}
                })
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Error al identificar acciones: {e}")
            return [{"action": "error", "priority": 1, "message": str(e)}]
    
    def _execute_action(self, action: Dict[str, Any]) -> Any:
        """Ejecutar acción específica de validación"""
        try:
            action_name = action["action"]
            parameters = action.get("parameters", {})
            
            self.logger.info(f"Ejecutando acción: {action_name}")
            
            if action_name == "validate_code_syntax":
                return self._validate_code_syntax(**parameters)
            elif action_name == "compile_project":
                return self._compile_project(**parameters)
            elif action_name == "run_tests":
                return self._run_tests(**parameters)
            elif action_name == "check_code_coverage":
                return self._check_code_coverage(**parameters)
            elif action_name == "validate_test_structure":
                return self._validate_test_structure(**parameters)
            elif action_name == "check_best_practices":
                return self._check_best_practices(**parameters)
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
            "validate_code_syntax": "Valida la sintaxis de archivos de código C# y detecta errores de compilación",
            "run_tests": "Ejecuta las pruebas unitarias del proyecto y reporta resultados",
            "check_code_coverage": "Verifica la cobertura de código de las pruebas unitarias",
            "validate_test_structure": "Valida que la estructura de las pruebas siga las mejores prácticas",
            "check_best_practices": "Verifica que el código siga las mejores prácticas de testing",
            "compile_project": "Compila el proyecto .NET y reporta errores de compilación"
        }
        return descriptions.get(tool_name, f"Herramienta: {tool_name}")
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Crear template de prompt para el agente"""
        template = """
Eres un agente especializado en validación de código y pruebas unitarias para .NET. Tu tarea es validar que el código generado sea correcto, funcional y siga las mejores prácticas.

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
    def _validate_code_syntax(self, target_files: List[str]) -> Dict[str, Any]:
        """Validar sintaxis de código"""
        try:
            validation_results = []
            
            for file_path in target_files:
                try:
                    content = code_file_manager.read_code_file(file_path)
                    
                    # Validaciones básicas de sintaxis
                    syntax_checks = {
                        "has_namespace": "namespace " in content,
                        "has_class": "class " in content,
                        "balanced_braces": content.count("{") == content.count("}"),
                        "balanced_parentheses": content.count("(") == content.count(")"),
                        "has_using_statements": "using " in content,
                        "valid_csharp_keywords": self._check_csharp_keywords(content)
                    }
                    
                    validation_results.append({
                        "file_path": file_path,
                        "syntax_valid": all(syntax_checks.values()),
                        "checks": syntax_checks,
                        "issues": [k for k, v in syntax_checks.items() if not v]
                    })
                    
                except Exception as e:
                    validation_results.append({
                        "file_path": file_path,
                        "syntax_valid": False,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "validation_results": validation_results,
                "overall_valid": all(r.get("syntax_valid", False) for r in validation_results)
            }
            
        except Exception as e:
            self.logger.error(f"Error al validar sintaxis: {e}")
            return {"success": False, "error": str(e)}
    
    def _compile_project(self, project_path: str) -> Dict[str, Any]:
        """Compilar proyecto"""
        try:
            result = command_executor.build_project(project_path)
            
            return {
                "success": result["success"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "return_code": result["return_code"],
                "compilation_successful": result["success"]
            }
            
        except Exception as e:
            self.logger.error(f"Error al compilar proyecto: {e}")
            return {"success": False, "error": str(e)}
    
    def _run_tests(self, project_path: str) -> Dict[str, Any]:
        """Ejecutar pruebas"""
        try:
            result = command_executor.run_tests(project_path)
            
            # Parsear resultados de pruebas
            test_results = self._parse_test_results(result["stdout"])
            
            return {
                "success": result["success"],
                "test_results": test_results,
                "stdout": result["stdout"],
                "stderr": result["stderr"]
            }
            
        except Exception as e:
            self.logger.error(f"Error al ejecutar pruebas: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_code_coverage(self, project_path: str) -> Dict[str, Any]:
        """Verificar cobertura de código"""
        try:
            result = command_executor.get_coverage(project_path)
            
            # Parsear resultados de cobertura
            coverage_results = self._parse_coverage_results(result["stdout"])
            
            return {
                "success": result["success"],
                "coverage_results": coverage_results,
                "stdout": result["stdout"]
            }
            
        except Exception as e:
            self.logger.error(f"Error al verificar cobertura: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_test_structure(self, target_files: List[str]) -> Dict[str, Any]:
        """Validar estructura de pruebas"""
        try:
            validation_results = []
            
            for file_path in target_files:
                try:
                    content = code_file_manager.read_code_file(file_path)
                    
                    # Validaciones de estructura de pruebas
                    structure_checks = {
                        "has_test_class": any(attr in content for attr in ["[TestClass]", "[Test]", "class"]),
                        "has_test_methods": any(attr in content for attr in ["[Test]", "[TestMethod]", "[Fact]"]),
                        "has_assertions": "Assert." in content,
                        "has_using_statements": "using " in content,
                        "proper_naming": self._check_test_naming(content),
                        "has_setup_methods": any(attr in content for attr in ["[SetUp]", "[TestInitialize]"])
                    }
                    
                    validation_results.append({
                        "file_path": file_path,
                        "structure_valid": all(structure_checks.values()),
                        "checks": structure_checks,
                        "issues": [k for k, v in structure_checks.items() if not v]
                    })
                    
                except Exception as e:
                    validation_results.append({
                        "file_path": file_path,
                        "structure_valid": False,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "validation_results": validation_results,
                "overall_valid": all(r.get("structure_valid", False) for r in validation_results)
            }
            
        except Exception as e:
            self.logger.error(f"Error al validar estructura: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_best_practices(self, target_files: List[str]) -> Dict[str, Any]:
        """Verificar mejores prácticas"""
        try:
            validation_results = []
            
            for file_path in target_files:
                try:
                    content = code_file_manager.read_code_file(file_path)
                    
                    # Verificaciones de mejores prácticas
                    best_practices_checks = {
                        "has_comments": "//" in content or "/*" in content,
                        "proper_indentation": self._check_indentation(content),
                        "no_hardcoded_values": not self._has_hardcoded_values(content),
                        "proper_mocking": "Mock<" in content or "new Mock" in content,
                        "test_isolation": self._check_test_isolation(content),
                        "meaningful_assertions": self._check_meaningful_assertions(content)
                    }
                    
                    validation_results.append({
                        "file_path": file_path,
                        "best_practices_valid": all(best_practices_checks.values()),
                        "checks": best_practices_checks,
                        "issues": [k for k, v in best_practices_checks.items() if not v]
                    })
                    
                except Exception as e:
                    validation_results.append({
                        "file_path": file_path,
                        "best_practices_valid": False,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "validation_results": validation_results,
                "overall_valid": all(r.get("best_practices_valid", False) for r in validation_results)
            }
            
        except Exception as e:
            self.logger.error(f"Error al verificar mejores prácticas: {e}")
            return {"success": False, "error": str(e)}
    
    # Métodos auxiliares
    def _check_csharp_keywords(self, content: str) -> bool:
        """Verificar que use palabras clave válidas de C#"""
        # Implementación básica
        invalid_keywords = ["var", "let", "const"]  # Ejemplo
        return not any(keyword in content for keyword in invalid_keywords)
    
    def _parse_test_results(self, stdout: str) -> Dict[str, Any]:
        """Parsear resultados de pruebas"""
        # Implementación básica
        return {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0
        }
    
    def _parse_coverage_results(self, stdout: str) -> Dict[str, Any]:
        """Parsear resultados de cobertura"""
        # Implementación básica
        return {
            "line_coverage": 0.0,
            "branch_coverage": 0.0,
            "method_coverage": 0.0
        }
    
    def _check_test_naming(self, content: str) -> bool:
        """Verificar naming de pruebas"""
        # Implementación básica
        return "Test" in content or "Should" in content
    
    def _check_indentation(self, content: str) -> bool:
        """Verificar indentación"""
        # Implementación básica
        lines = content.split('\n')
        return all(line.startswith('    ') or not line.strip() for line in lines if line.strip())
    
    def _has_hardcoded_values(self, content: str) -> bool:
        """Verificar valores hardcodeados"""
        # Implementación básica
        hardcoded_patterns = ['"test"', "'test'", "123", "true", "false"]
        return any(pattern in content for pattern in hardcoded_patterns)
    
    def _check_test_isolation(self, content: str) -> bool:
        """Verificar aislamiento de pruebas"""
        # Implementación básica
        return "new " in content or "Mock<" in content
    
    def _check_meaningful_assertions(self, content: str) -> bool:
        """Verificar assertions significativas"""
        # Implementación básica
        return "Assert." in content and "Assert.True" not in content
    
    def _save_validation_result(self, task_id: str, result: Any):
        """Guardar resultado de validación en memoria"""
        try:
            self.vector_memory.add_entry(
                content=f"Resultado de validación para tarea {task_id}",
                metadata={
                    "task_id": task_id,
                    "result_type": type(result).__name__,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error al guardar resultado de validación: {e}")
    
    def validate_code(self, code: str) -> str:
        """Método simplificado para validar código directamente usando memoria"""
        try:
            self.logger.info("Iniciando validación de código usando memoria")
            
            # Usar LLM directamente para validación si está disponible
            if self.llm:
                return self._validate_with_llm(code)
            else:
                # Realizar validación básica
                return self._perform_basic_validation(code)
                
        except Exception as e:
            self.logger.error(f"Error en validación de código: {e}")
            return self._perform_basic_validation(code)
    
    def _validate_with_llm(self, code: str) -> str:
        """Validar código usando LLM directamente"""
        try:
            # Crear prompt para validación
            validation_prompt = f"""
Eres un experto en validación de código C# y pruebas unitarias. Analiza el siguiente código y proporciona un reporte de validación detallado.

CÓDIGO A VALIDAR:
{code}

Por favor, proporciona un análisis que incluya:

1. **Sintaxis**: ¿El código tiene errores de sintaxis?
2. **Funcionalidad**: ¿El código es funcional y lógicamente correcto?
3. **Mejores Prácticas**: ¿Sigue las mejores prácticas de C# y testing?
4. **Estructura**: ¿La estructura del código es apropiada?
5. **Problemas Detectados**: Lista cualquier problema encontrado
6. **Recomendaciones**: Sugerencias para mejorar el código

Formato de respuesta:
- ✅ para elementos correctos
- ⚠️ para advertencias
- ❌ para errores críticos

Responde de manera concisa pero completa.
"""
            
            # Usar LLM para validación
            response = self.llm.invoke(validation_prompt)
            return response.content
            
        except Exception as e:
            self.logger.error(f"Error al validar con LLM: {e}")
            return self._perform_basic_validation(code)
    
    def _perform_basic_validation(self, code: str) -> str:
        """Realizar validación básica del código"""
        issues = []
        
        # Verificar sintaxis básica
        if not code.strip():
            issues.append("❌ Código vacío")
        
        # Verificar que tenga clases
        if "class " not in code:
            issues.append("⚠️  No se encontraron clases")
        
        # Verificar que tenga métodos
        if "public " not in code and "private " not in code:
            issues.append("⚠️  No se encontraron métodos públicos o privados")
        
        # Verificar indentación
        if not self._check_indentation(code):
            issues.append("⚠️  Problemas de indentación detectados")
        
        if not issues:
            return "✅ Validación básica completada sin errores detectados"
        else:
            return "\n".join(issues)


# Instancia global del agente validador
validation_agent = ValidationAgent()
