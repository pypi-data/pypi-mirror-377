"""
Gestor avanzado de LLMs
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
import asyncio
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import AzureOpenAI
from openai import OpenAI
import google.generativeai as genai

from utils.logging import get_logger
from utils.config import get_config


class DeepSeekLLM:
    """Wrapper para DeepSeek usando OpenAI API compatible"""
    
    def __init__(self, api_key: str, model: str = "deepseek-coder", 
                 temperature: float = 0.1, max_tokens: int = 4000, timeout: int = 30):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
    
    def invoke(self, prompt: str) -> Any:
        """Invocar modelo de forma síncrona"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            
            # Crear objeto similar a LangChain
            class MockResponse:
                def __init__(self, content):
                    self.content = content
            
            return MockResponse(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error en DeepSeek invoke: {e}")
            raise
    
    async def ainvoke(self, prompt: str) -> Any:
        """Invocar modelo de forma asíncrona"""
        try:
            response = await self.client.chat.completions.acreate(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            
            # Crear objeto similar a LangChain
            class MockResponse:
                def __init__(self, content):
                    self.content = content
            
            return MockResponse(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error en DeepSeek ainvoke: {e}")
            raise


class GeminiLLM:
    """Wrapper para Gemini usando Google AI"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", 
                 temperature: float = 0.1, max_tokens: int = 4000, timeout: int = 30):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
    
    def invoke(self, prompt: str) -> Any:
        """Invocar modelo de forma síncrona"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            
            # Crear objeto similar a LangChain
            class MockResponse:
                def __init__(self, content):
                    self.content = content
            
            return MockResponse(response.text)
            
        except Exception as e:
            logger.error(f"Error en Gemini invoke: {e}")
            raise
    
    async def ainvoke(self, prompt: str) -> Any:
        """Invocar modelo de forma asíncrona"""
        try:
            # Gemini no tiene soporte asíncrono nativo, usar sync
            return self.invoke(prompt)
            
        except Exception as e:
            logger.error(f"Error en Gemini ainvoke: {e}")
            raise

logger = get_logger("llm-manager")


class LLMProvider(Enum):
    """Proveedores de LLM soportados"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"


@dataclass
class LLMConfig:
    """Configuración de LLM"""
    provider: LLMProvider
    model: str
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 30
    api_key: Optional[str] = None
    endpoint: Optional[str] = None


class LLMManager:
    """Gestor avanzado de LLMs con múltiples proveedores"""
    
    def __init__(self):
        self.logger = logger
        self.config = get_config()
        self.llms: Dict[str, Any] = {}
        self.current_llm: Optional[Any] = None
        self._setup_default_llms()
    
    def _setup_default_llms(self):
        """Configurar LLMs por defecto"""
        try:
            # LLM principal basado en configuración
            if self.config.ai.provider == "openai":
                self.llms["primary"] = ChatOpenAI(
                    model=self.config.ai.model,
                    temperature=self.config.ai.temperature,
                    max_tokens=self.config.ai.max_tokens,
                    timeout=self.config.ai.timeout
                )
                self.current_llm = self.llms["primary"]
                
            elif self.config.ai.provider == "deepseek":
                # Verificar si hay API key de DeepSeek
                deepseek_key = getattr(self.config, 'deepseek_api_key', None)
                if not deepseek_key:
                    self.logger.warning("DEEPSEEK_API_KEY no configurado, usando OpenAI como fallback")
                    # Intentar usar OpenAI como fallback
                    try:
                        self.llms["primary"] = ChatOpenAI(
                            model="gpt-3.5-turbo",
                            temperature=self.config.ai.temperature,
                            max_tokens=self.config.ai.max_tokens,
                            timeout=self.config.ai.timeout
                        )
                    except Exception as e:
                        self.logger.error(f"No se pudo configurar OpenAI como fallback: {e}")
                        # Crear un LLM mock para evitar errores
                        self.llms["primary"] = None
                else:
                    self.llms["primary"] = DeepSeekLLM(
                        api_key=deepseek_key,
                        model=self.config.ai.model,
                        temperature=self.config.ai.temperature,
                        max_tokens=self.config.ai.max_tokens,
                        timeout=self.config.ai.timeout
                    )
                self.current_llm = self.llms["primary"]
                
            elif self.config.ai.provider == "gemini":
                # Verificar si hay API key de Gemini
                gemini_key = getattr(self.config, 'gemini_api_key', None)
                if not gemini_key:
                    self.logger.warning("GEMINI_API_KEY no configurado, usando OpenAI como fallback")
                    # Intentar usar OpenAI como fallback
                    try:
                        self.llms["primary"] = ChatOpenAI(
                            model="gpt-3.5-turbo",
                            temperature=self.config.ai.temperature,
                            max_tokens=self.config.ai.max_tokens,
                            timeout=self.config.ai.timeout
                        )
                    except Exception as e:
                        self.logger.error(f"No se pudo configurar OpenAI como fallback: {e}")
                        # Crear un LLM mock para evitar errores
                        self.llms["primary"] = None
                else:
                    self.llms["primary"] = GeminiLLM(
                        api_key=gemini_key,
                        model=self.config.ai.model,
                        temperature=self.config.ai.temperature,
                        max_tokens=self.config.ai.max_tokens,
                        timeout=self.config.ai.timeout
                    )
                self.current_llm = self.llms["primary"]
            
            # LLM de respaldo (más rápido)
            if self.config.ai.provider == "deepseek":
                # Usar DeepSeek para respaldo también
                deepseek_key = getattr(self.config, 'deepseek_api_key', None)
                if deepseek_key:
                    self.llms["fast"] = DeepSeekLLM(
                        api_key=deepseek_key,
                        model="deepseek-chat",
                        temperature=0.1,
                        max_tokens=2000,
                        timeout=15
                    )
                else:
                    self.llms["fast"] = ChatOpenAI(
                        model="gpt-3.5-turbo",
                        temperature=0.1,
                        max_tokens=2000,
                        timeout=15
                    )
            else:
                self.llms["fast"] = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    max_tokens=2000,
                    timeout=15
                )
            
            # LLM especializado en código
            if self.config.ai.provider == "deepseek":
                # DeepSeek Coder es excelente para código
                deepseek_key = getattr(self.config, 'deepseek_api_key', None)
                if deepseek_key:
                    self.llms["code"] = DeepSeekLLM(
                        api_key=deepseek_key,
                        model="deepseek-coder",
                        temperature=0.05,
                        max_tokens=6000,
                        timeout=45
                    )
                else:
                    self.llms["code"] = ChatOpenAI(
                        model="gpt-4",
                        temperature=0.05,
                        max_tokens=6000,
                        timeout=45
                    )
            else:
                self.llms["code"] = ChatOpenAI(
                    model="gpt-4",
                    temperature=0.05,
                    max_tokens=6000,
                    timeout=45
                )
            
            self.logger.info(f"LLMs configurados correctamente con proveedor: {self.config.ai.provider}")
            
        except Exception as e:
            self.logger.error(f"Error al configurar LLMs: {e}")
            raise
    
    def get_llm(self, llm_type: str = "primary") -> Any:
        """Obtener LLM por tipo"""
        if llm_type not in self.llms:
            self.logger.warning(f"LLM tipo '{llm_type}' no encontrado, usando primary")
            llm_type = "primary"
        
        return self.llms[llm_type]
    
    def switch_llm(self, llm_type: str):
        """Cambiar LLM actual"""
        if llm_type in self.llms:
            self.current_llm = self.llms[llm_type]
            self.logger.info(f"LLM cambiado a: {llm_type}")
        else:
            self.logger.warning(f"LLM tipo '{llm_type}' no encontrado")
    
    async def generate_async(self, prompt: str, llm_type: str = "primary") -> str:
        """Generar respuesta de forma asíncrona"""
        try:
            llm = self.get_llm(llm_type)
            response = await llm.ainvoke(prompt)
            return response.content
            
        except Exception as e:
            self.logger.error(f"Error en generación asíncrona: {e}")
            raise
    
    def generate_batch(self, prompts: List[str], llm_type: str = "primary") -> List[str]:
        """Generar respuestas en lote"""
        try:
            llm = self.get_llm(llm_type)
            responses = []
            
            for prompt in prompts:
                response = llm.invoke(prompt)
                responses.append(response.content)
            
            self.logger.info(f"Generadas {len(responses)} respuestas en lote")
            return responses
            
        except Exception as e:
            self.logger.error(f"Error en generación en lote: {e}")
            raise
    
    def get_available_llms(self) -> List[str]:
        """Obtener LLMs disponibles"""
        return list(self.llms.keys())
    
    def get_llm_info(self, llm_type: str) -> Dict[str, Any]:
        """Obtener información del LLM"""
        if llm_type not in self.llms:
            return {}
        
        llm = self.llms[llm_type]
        return {
            "type": llm_type,
            "model": getattr(llm, 'model_name', 'unknown'),
            "temperature": getattr(llm, 'temperature', 0.1),
            "max_tokens": getattr(llm, 'max_tokens', 4000),
            "timeout": getattr(llm, 'timeout', 30)
        }
