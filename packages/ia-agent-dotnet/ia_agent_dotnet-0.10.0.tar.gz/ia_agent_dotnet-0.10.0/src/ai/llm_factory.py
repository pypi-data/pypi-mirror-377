"""
Factory para crear instancias de LLM según la configuración global
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Optional, Union
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from ai.llm_manager import DeepSeekLLM, GeminiLLM
from config.global_config import GlobalConfig
from utils.config import Config
from utils.logging import get_logger

logger = get_logger("llm-factory")


class LLMFactory:
    """Factory para crear instancias de LLM según la configuración"""
    
    @staticmethod
    def create_llm(config: GlobalConfig) -> Union[ChatOpenAI, ChatGoogleGenerativeAI, DeepSeekLLM, GeminiLLM]:
        """Crear instancia de LLM según la configuración"""
        try:
            provider = config.ai_provider.lower()
            model = config.ai_model
            temperature = config.ai_temperature
            max_tokens = config.ai_max_tokens
            
            logger.info(f"Creando LLM: {provider} - {model}")
            
            if provider == "openai":
                if not config.openai_api_key:
                    raise ValueError("OpenAI API key no configurada")
                
                return ChatOpenAI(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    openai_api_key=config.openai_api_key
                )
            
            elif provider == "deepseek":
                if not config.deepseek_api_key:
                    raise ValueError("DeepSeek API key no configurada")
                
                return DeepSeekLLM(
                    api_key=config.deepseek_api_key,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            
            elif provider == "gemini":
                if not config.gemini_api_key:
                    raise ValueError("Gemini API key no configurada")
                
                return ChatGoogleGenerativeAI(
                    model=model,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    google_api_key=config.gemini_api_key
                )
            
            else:
                raise ValueError(f"Proveedor de IA no soportado: {provider}")
                
        except Exception as e:
            logger.error(f"Error al crear LLM: {e}")
            raise
    
    @staticmethod
    def create_langchain_llm(config: Union[Config, GlobalConfig]) -> Union[ChatOpenAI, ChatGoogleGenerativeAI]:
        """Crear instancia de LLM compatible con LangChain"""
        try:
            # Obtener configuración global si se pasa Config
            if isinstance(config, Config):
                from config.global_config import global_config_manager
                global_config = global_config_manager.get_config()
            else:
                global_config = config
            
            provider = global_config.ai_provider.lower()
            model = global_config.ai_model
            temperature = global_config.ai_temperature
            max_tokens = global_config.ai_max_tokens
            
            logger.info(f"Creando LangChain LLM: {provider} - {model}")
            
            if provider == "openai":
                if not global_config.openai_api_key:
                    raise ValueError("OpenAI API key no configurada")
                
                return ChatOpenAI(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    openai_api_key=global_config.openai_api_key
                )
            
            elif provider == "gemini":
                if not global_config.gemini_api_key:
                    raise ValueError("Gemini API key no configurada")
                
                return ChatGoogleGenerativeAI(
                    model=model,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    google_api_key=global_config.gemini_api_key
                )
            
            elif provider == "deepseek":
                # DeepSeek usa la API de OpenAI, así que podemos usar ChatOpenAI
                if not global_config.deepseek_api_key:
                    raise ValueError("DeepSeek API key no configurada")
                
                return ChatOpenAI(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    openai_api_key=global_config.deepseek_api_key,
                    openai_api_base="https://api.deepseek.com/v1"
                )
            
            else:
                raise ValueError(f"Proveedor de IA no soportado: {provider}")
                
        except Exception as e:
            logger.error(f"Error al crear LangChain LLM: {e}")
            raise
