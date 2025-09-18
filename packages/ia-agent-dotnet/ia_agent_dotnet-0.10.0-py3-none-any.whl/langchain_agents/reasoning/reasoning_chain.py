"""
Cadena de razonamiento para análisis de código
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from utils.logging import get_logger

logger = get_logger("reasoning-chain")


class ReasoningChain:
    """Cadena de razonamiento para análisis de código"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or self._create_default_llm()
        self.logger = logger
        self.chains = {}
        self._setup_chains()
    
    def _create_default_llm(self) -> ChatOpenAI:
        """Crear LLM por defecto"""
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            max_tokens=4000
        )
    
    def _setup_chains(self):
        """Configurar cadenas de razonamiento"""
        try:
            # Cadena de análisis de código
            analysis_prompt = PromptTemplate(
                input_variables=["code", "context"],
                template="""
Analiza el siguiente código C# y proporciona un análisis detallado:

Código:
{code}

Contexto:
{context}

Proporciona:
1. Análisis de la estructura del código
2. Identificación de patrones de diseño
3. Dependencias y referencias
4. Complejidad y posibles mejoras
5. Recomendaciones para pruebas unitarias

Análisis:
"""
            )
            
            self.chains["analysis"] = LLMChain(
                llm=self.llm,
                prompt=analysis_prompt
            )
            
            # Cadena de generación de pruebas
            test_generation_prompt = PromptTemplate(
                input_variables=["code", "analysis", "framework"],
                template="""
Basándote en el código y análisis proporcionados, genera pruebas unitarias completas:

Código:
{code}

Análisis:
{analysis}

Framework: {framework}

Genera:
1. Pruebas para todos los métodos públicos
2. Casos de prueba para casos normales y edge cases
3. Mocks para dependencias
4. Assertions apropiadas
5. Documentación de las pruebas

Pruebas unitarias:
"""
            )
            
            self.chains["test_generation"] = LLMChain(
                llm=self.llm,
                prompt=test_generation_prompt
            )
            
            # Cadena de validación
            validation_prompt = PromptTemplate(
                input_variables=["code", "tests"],
                template="""
Valida las siguientes pruebas unitarias contra el código:

Código:
{code}

Pruebas:
{tests}

Proporciona:
1. Verificación de cobertura de pruebas
2. Identificación de casos faltantes
3. Validación de la calidad de las pruebas
4. Sugerencias de mejora
5. Puntuación de calidad (1-10)

Validación:
"""
            )
            
            self.chains["validation"] = LLMChain(
                llm=self.llm,
                prompt=validation_prompt
            )
            
            self.logger.info("Cadenas de razonamiento configuradas")
            
        except Exception as e:
            self.logger.error(f"Error al configurar cadenas: {e}")
            raise
    
    def analyze_code(self, code: str, context: str = "") -> str:
        """Analizar código"""
        try:
            result = self.chains["analysis"].run(code=code, context=context)
            self.logger.info("Análisis de código completado")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al analizar código: {e}")
            raise
    
    def generate_tests(self, code: str, analysis: str, framework: str = "xunit") -> str:
        """Generar pruebas unitarias"""
        try:
            result = self.chains["test_generation"].run(
                code=code,
                analysis=analysis,
                framework=framework
            )
            self.logger.info("Generación de pruebas completada")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al generar pruebas: {e}")
            raise
    
    def validate_tests(self, code: str, tests: str) -> str:
        """Validar pruebas unitarias"""
        try:
            result = self.chains["validation"].run(code=code, tests=tests)
            self.logger.info("Validación de pruebas completada")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al validar pruebas: {e}")
            raise
    
    def get_available_chains(self) -> List[str]:
        """Obtener cadenas disponibles"""
        return list(self.chains.keys())
