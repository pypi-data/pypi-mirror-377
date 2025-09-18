#!/usr/bin/env python3
"""
Configuración global para IA Agent
IA Agent para Generación de Pruebas Unitarias .NET
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class GlobalConfig(BaseModel):
    """Configuración global del agente"""
    
    # Configuración de IA
    openai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    ai_provider: str = "deepseek"
    ai_model: str = "deepseek-coder"
    ai_temperature: float = 0.1
    ai_max_tokens: int = 4000
    
    # Configuración de logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Configuración de memoria
    memory_cache_size: int = 1000
    chromadb_persist_directory: str = "./memory/vector"
    
    # Configuración de agentes
    max_concurrent_agents: int = 3
    agent_timeout: int = 60
    
    # Configuración de archivos
    temp_directory: str = "./temp"
    output_directory: str = "./output"
    allowed_file_extensions: str = ".cs,.csproj,.sln"
    
    # Configuración de .NET
    dotnet_path: str = "dotnet"
    
    # Configuración de desarrollo
    debug_mode: bool = False
    enable_telemetry: bool = False


class GlobalConfigManager:
    """Manager para configuración global del agente"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / "ia-agent-config.json"
        self.config = self._load_config()
    
    def _get_config_directory(self) -> Path:
        """Obtener directorio de configuración global"""
        # En Windows: %APPDATA%\ia-agent
        # En Linux/Mac: ~/.config/ia-agent
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'ia-agent'
        else:  # Linux/Mac
            config_dir = Path.home() / '.config' / 'ia-agent'
        
        # Crear directorio si no existe
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def _load_config(self) -> GlobalConfig:
        """Cargar configuración desde archivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return GlobalConfig(**config_data)
            except Exception as e:
                self.logger.warning(f"Error al cargar configuración global: {e}")
                return GlobalConfig()
        else:
            return GlobalConfig()
    
    def save_config(self, config: GlobalConfig) -> bool:
        """Guardar configuración en archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config.dict(), f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuración global guardada en: {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error al guardar configuración global: {e}")
            return False
    
    def update_config(self, **kwargs) -> bool:
        """Actualizar configuración"""
        try:
            # Actualizar configuración
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    self.logger.info(f"Configuración actualizada: {key} = {value}")
            
            # Guardar cambios
            return self.save_config(self.config)
        except Exception as e:
            self.logger.error(f"Error al actualizar configuración: {e}")
            return False
    
    def get_config(self) -> GlobalConfig:
        """Obtener configuración actual"""
        return self.config
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Obtener API key para un proveedor específico"""
        if provider.lower() == "openai":
            return self.config.openai_api_key
        elif provider.lower() == "deepseek":
            return self.config.deepseek_api_key
        elif provider.lower() == "gemini":
            return self.config.gemini_api_key
        return None
    
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """Establecer API key para un proveedor específico"""
        if provider.lower() == "openai":
            return self.update_config(openai_api_key=api_key)
        elif provider.lower() == "deepseek":
            return self.update_config(deepseek_api_key=api_key)
        elif provider.lower() == "gemini":
            return self.update_config(gemini_api_key=api_key)
        return False
    
    def is_configured(self) -> bool:
        """Verificar si el agente está configurado"""
        provider = self.config.ai_provider.lower()
        api_key = self.get_api_key(provider)
        return api_key is not None and len(api_key) > 10
    
    def get_config_info(self) -> Dict[str, Any]:
        """Obtener información de configuración"""
        return {
            "config_file": str(self.config_file),
            "ai_provider": self.config.ai_provider,
            "ai_model": self.config.ai_model,
            "is_configured": self.is_configured(),
            "has_openai_key": bool(self.config.openai_api_key),
            "has_deepseek_key": bool(self.config.deepseek_api_key),
            "has_gemini_key": bool(self.config.gemini_api_key),
        }
    
    def reset_config(self) -> bool:
        """Resetear configuración a valores por defecto"""
        try:
            self.config = GlobalConfig()
            return self.save_config(self.config)
        except Exception as e:
            self.logger.error(f"Error al resetear configuración: {e}")
            return False


# Instancia global del manager de configuración
global_config_manager = GlobalConfigManager()
