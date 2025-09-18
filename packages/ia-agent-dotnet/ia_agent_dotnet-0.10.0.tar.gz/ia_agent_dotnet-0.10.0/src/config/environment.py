#!/usr/bin/env python3
"""
Configuración de entorno para el sistema
IA Agent para Generación de Pruebas Unitarias .NET
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings

from .global_config import global_config_manager


class EnvironmentConfig(BaseSettings):
    """Configuración de entorno del sistema"""
    
    # Configuración de IA
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    deepseek_api_key: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")
    gemini_api_key: Optional[str] = Field(None, env="GEMINI_API_KEY")
    ai_provider: str = Field("deepseek", env="AI_PROVIDER")
    ai_model: str = Field("deepseek-coder", env="AI_MODEL")
    ai_temperature: float = Field(0.1, env="AI_TEMPERATURE")
    ai_max_tokens: int = Field(4000, env="AI_MAX_TOKENS")
    
    # Configuración de logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")
    log_format: str = Field("%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s", env="LOG_FORMAT")
    
    # Configuración de ChromaDB
    chromadb_persist_directory: str = Field("./memory/vector", env="CHROMADB_PERSIST_DIRECTORY")
    chromadb_collection_name: str = Field("ia_agent_memory", env="CHROMADB_COLLECTION_NAME")
    chromadb_anonymized_telemetry: bool = Field(False, env="CHROMADB_ANONYMIZED_TELEMETRY")
    
    # Configuración de .NET
    dotnet_path: Optional[str] = Field(None, env="DOTNET_PATH")
    dotnet_timeout: int = Field(30, env="DOTNET_TIMEOUT")
    
    # Configuración de archivos
    temp_directory: str = Field("./temp", env="TEMP_DIRECTORY")
    output_directory: str = Field("./output", env="OUTPUT_DIRECTORY")
    max_file_size: int = Field(10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    # Configuración de rendimiento
    max_concurrent_agents: int = Field(3, env="MAX_CONCURRENT_AGENTS")
    agent_timeout: int = Field(60, env="AGENT_TIMEOUT")
    memory_cache_size: int = Field(1000, env="MEMORY_CACHE_SIZE")
    
    # Configuración de seguridad
    enable_file_validation: bool = Field(True, env="ENABLE_FILE_VALIDATION")
    allowed_file_extensions: str = Field(".cs,.csproj,.sln", env="ALLOWED_FILE_EXTENSIONS")
    
    # Configuración de desarrollo
    debug_mode: bool = Field(False, env="DEBUG_MODE")
    enable_telemetry: bool = Field(False, env="ENABLE_TELEMETRY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class EnvironmentManager:
    """Manager para configuración de entorno"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_config()
        self._setup_directories()
        self._validate_config()
    
    def _load_config(self):
        """Cargar configuración desde global y local"""
        # Primero cargar configuración local (archivo .env si existe)
        self.config = EnvironmentConfig()
        
        # Luego sobrescribir con configuración global si está disponible
        global_config = global_config_manager.get_config()
        
        # Actualizar con valores globales si no están definidos localmente
        if not self.config.openai_api_key and global_config.openai_api_key:
            self.config.openai_api_key = global_config.openai_api_key
        if not self.config.deepseek_api_key and global_config.deepseek_api_key:
            self.config.deepseek_api_key = global_config.deepseek_api_key
        if not self.config.gemini_api_key and global_config.gemini_api_key:
            self.config.gemini_api_key = global_config.gemini_api_key
        
        # Usar configuración global para otros valores si no están definidos localmente
        if self.config.ai_provider == "deepseek" and global_config.ai_provider:
            self.config.ai_provider = global_config.ai_provider
        if self.config.ai_model == "deepseek-coder" and global_config.ai_model:
            self.config.ai_model = global_config.ai_model
    
    def _setup_directories(self):
        """Crear directorios necesarios"""
        directories = [
            self.config.chromadb_persist_directory,
            self.config.temp_directory,
            self.config.output_directory,
            "./logs",
            "./memory"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Directorio creado/verificado: {directory}")
    
    def _validate_config(self):
        """Validar configuración"""
        # Validar API key según el proveedor
        if self.config.ai_provider == "openai" and not self.config.openai_api_key:
            self.logger.warning("OPENAI_API_KEY no configurado. Funcionalidad de IA limitada.")
        elif self.config.ai_provider == "deepseek" and not self.config.deepseek_api_key:
            self.logger.warning("DEEPSEEK_API_KEY no configurado. Funcionalidad de IA limitada.")
        elif self.config.ai_provider == "gemini" and not self.config.gemini_api_key:
            self.logger.warning("GEMINI_API_KEY no configurado. Funcionalidad de IA limitada.")
        
        # Validar extensiones de archivo
        if self.config.allowed_file_extensions:
            self.config.allowed_file_extensions = [
                ext.strip() for ext in self.config.allowed_file_extensions.split(",")
            ]
        
        # Validar directorio de .NET
        if self.config.dotnet_path and not Path(self.config.dotnet_path).exists():
            self.logger.warning(f"Directorio de .NET no encontrado: {self.config.dotnet_path}")
    
    def get_config(self) -> EnvironmentConfig:
        """Obtener configuración"""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Actualizar configuración"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"Configuración actualizada: {key} = {value}")
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Obtener información del entorno"""
        return {
            "ai_provider": self.config.ai_provider,
            "ai_model": self.config.ai_model,
            "log_level": self.config.log_level,
            "debug_mode": self.config.debug_mode,
            "max_concurrent_agents": self.config.max_concurrent_agents,
            "chromadb_persist_directory": self.config.chromadb_persist_directory,
            "temp_directory": self.config.temp_directory,
            "output_directory": self.config.output_directory
        }
    
    def is_production(self) -> bool:
        """Verificar si está en modo producción"""
        return not self.config.debug_mode and self.config.log_level.upper() in ["WARNING", "ERROR"]
    
    def is_development(self) -> bool:
        """Verificar si está en modo desarrollo"""
        return self.config.debug_mode or self.config.log_level.upper() in ["DEBUG", "INFO"]


# Instancia global del manager de entorno
environment_manager = EnvironmentManager()
