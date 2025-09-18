"""
Agente de planificación para tareas complejas
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from utils.logging import get_logger

logger = get_logger("planning-agent")


class PlanningAgent:
    """Agente de planificación para tareas complejas"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or self._create_default_llm()
        self.logger = logger
        self.planning_chain = None
        self._setup_planning_chain()
    
    def _create_default_llm(self) -> ChatOpenAI:
        """Crear LLM por defecto"""
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            max_tokens=4000
        )
    
    def _setup_planning_chain(self):
        """Configurar cadena de planificación"""
        try:
            planning_prompt = PromptTemplate(
                input_variables=["task", "context", "constraints"],
                template="""
Eres un agente de planificación especializado en tareas de desarrollo de software y generación de pruebas unitarias.

Tarea: {task}
Contexto: {context}
Restricciones: {constraints}

Crea un plan detallado que incluya:

1. **Análisis de la tarea**
   - Entendimiento del objetivo
   - Identificación de componentes involucrados
   - Análisis de dependencias

2. **Estrategia de implementación**
   - Pasos principales
   - Orden de ejecución
   - Puntos de verificación

3. **Plan de trabajo detallado**
   - Tareas específicas
   - Tiempo estimado
   - Recursos necesarios
   - Criterios de éxito

4. **Gestión de riesgos**
   - Posibles problemas
   - Planes de contingencia
   - Mitigaciones

5. **Validación y testing**
   - Criterios de aceptación
   - Pruebas de validación
   - Métricas de calidad

Plan:
"""
            )
            
            self.planning_chain = LLMChain(
                llm=self.llm,
                prompt=planning_prompt
            )
            
            self.logger.info("Cadena de planificación configurada")
            
        except Exception as e:
            self.logger.error(f"Error al configurar cadena de planificación: {e}")
            raise
    
    def create_plan(self, task: str, context: str = "", constraints: str = "") -> str:
        """Crear plan para una tarea"""
        try:
            result = self.planning_chain.run(
                task=task,
                context=context,
                constraints=constraints
            )
            self.logger.info("Plan creado exitosamente")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al crear plan: {e}")
            raise
    
    def plan_test_generation(self, project_path: str, target_classes: List[str], framework: str = "xunit") -> str:
        """Planificar generación de pruebas para un proyecto"""
        try:
            task = f"Generar pruebas unitarias para las clases {', '.join(target_classes)} en el proyecto {project_path}"
            context = f"Framework de testing: {framework}. Proyecto .NET con múltiples clases."
            constraints = "Mantener cobertura de pruebas alta, seguir mejores prácticas, generar mocks apropiados"
            
            plan = self.create_plan(task, context, constraints)
            self.logger.info("Plan de generación de pruebas creado")
            return plan
            
        except Exception as e:
            self.logger.error(f"Error al planificar generación de pruebas: {e}")
            raise
    
    def plan_code_analysis(self, project_path: str, analysis_type: str = "comprehensive") -> str:
        """Planificar análisis de código"""
        try:
            task = f"Realizar análisis {analysis_type} del proyecto {project_path}"
            context = "Proyecto .NET con múltiples archivos, clases y dependencias"
            constraints = "Análisis detallado, identificación de patrones, recomendaciones de mejora"
            
            plan = self.create_plan(task, context, constraints)
            self.logger.info("Plan de análisis de código creado")
            return plan
            
        except Exception as e:
            self.logger.error(f"Error al planificar análisis de código: {e}")
            raise
    
    def get_capabilities(self) -> List[str]:
        """Obtener capacidades del agente de planificación"""
        return [
            "Planificación de tareas complejas",
            "Análisis de dependencias",
            "Gestión de riesgos",
            "Estimación de tiempo y recursos",
            "Creación de estrategias de implementación",
            "Planificación de testing y validación"
        ]
