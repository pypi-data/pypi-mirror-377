"""
Agente ReAct (Reasoning + Acting) con LangChain
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from utils.logging import get_logger

logger = get_logger("react-agent")


class ReActAgent:
    """Agente ReAct para razonamiento y acción"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or self._create_default_llm()
        self.logger = logger
        self.tools = []
        self.agent_executor = None
    
    def _create_default_llm(self) -> ChatOpenAI:
        """Crear LLM por defecto"""
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            max_tokens=4000
        )
    
    def add_tool(self, tool: Tool):
        """Agregar herramienta al agente"""
        self.tools.append(tool)
        self.logger.info(f"Herramienta agregada: {tool.name}")
    
    def setup_agent(self):
        """Configurar agente ReAct"""
        try:
            if not self.tools:
                raise ValueError("No hay herramientas disponibles")
            
            # Template de prompt para ReAct
            react_prompt = PromptTemplate.from_template("""
Eres un agente especializado en análisis y generación de pruebas unitarias para código .NET.

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

Question: {input}
Thought: {agent_scratchpad}
""")
            
            # Crear agente ReAct
            agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=react_prompt
            )
            
            # Crear ejecutor del agente
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=5,
                early_stopping_method="generate"
            )
            
            self.logger.info("Agente ReAct configurado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al configurar agente ReAct: {e}")
            raise
    
    def run(self, input_text: str) -> str:
        """Ejecutar agente con entrada"""
        try:
            if not self.agent_executor:
                self.setup_agent()
            
            result = self.agent_executor.invoke({"input": input_text})
            return result.get("output", "No se pudo procesar la entrada")
            
        except Exception as e:
            self.logger.error(f"Error al ejecutar agente: {e}")
            raise
    
    def get_capabilities(self) -> List[str]:
        """Obtener capacidades del agente"""
        return [
            "Análisis de código .NET",
            "Generación de pruebas unitarias",
            "Razonamiento paso a paso",
            "Uso de herramientas especializadas",
            "Validación de código generado"
        ]
