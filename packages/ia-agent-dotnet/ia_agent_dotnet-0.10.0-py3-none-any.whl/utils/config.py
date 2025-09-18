"""
Configuración y manejo de archivos de configuración
IA Agent para Generación de Pruebas Unitarias .NET
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class AIConfig(BaseModel):
    """Configuración de IA"""
    provider: str = Field(default="openai", description="Proveedor de IA")
    model: str = Field(default="gpt-4", description="Modelo de IA")
    temperature: float = Field(default=0.1, description="Temperatura del modelo")
    max_tokens: int = Field(default=4000, description="Máximo de tokens")
    timeout: int = Field(default=30, description="Timeout en segundos")
    
    # Configuración específica por proveedor
    openai_api_key: Optional[str] = Field(default=None, description="API Key de OpenAI")
    openai_organization: Optional[str] = Field(default=None, description="Organización de OpenAI")
    
    azure_endpoint: Optional[str] = Field(default=None, description="Endpoint de Azure OpenAI")
    azure_api_key: Optional[str] = Field(default=None, description="API Key de Azure")
    azure_api_version: str = Field(default="2024-02-15-preview", description="Versión de API de Azure")


class MemoryConfig(BaseModel):
    """Configuración de memoria"""
    type: str = Field(default="persistent", description="Tipo de memoria")
    storage_path: str = Field(default="./memory", description="Ruta de almacenamiento")
    
    # Memoria individual
    individual_buffer_size: int = Field(default=1000, description="Tamaño del buffer individual")
    individual_summary_threshold: int = Field(default=50, description="Umbral para resumen")
    individual_vector_store: str = Field(default="chroma", description="Vector store individual")
    
    # Memoria compartida
    shared_enabled: bool = Field(default=False, description="Memoria compartida habilitada")
    shared_storage_path: str = Field(default="./memory/shared", description="Ruta de memoria compartida")
    shared_sync_interval: int = Field(default=60, description="Intervalo de sincronización")


class TestingConfig(BaseModel):
    """Configuración de testing"""
    framework: str = Field(default="xunit", description="Framework de testing")
    auto_detect: bool = Field(default=True, description="Detección automática")
    
    patterns: list = Field(default=["repository", "service", "controller", "dto", "entity"], 
                          description="Patrones de código soportados")
    
    coverage_threshold: int = Field(default=80, description="Umbral de cobertura")
    generate_report: bool = Field(default=True, description="Generar reportes")
    report_format: str = Field(default="html", description="Formato de reporte")
    
    mock_framework: str = Field(default="moq", description="Framework de mocks")


class GenerationConfig(BaseModel):
    """Configuración de generación"""
    auto_format: bool = Field(default=True, description="Formateo automático")
    include_comments: bool = Field(default=True, description="Incluir comentarios")
    include_using_statements: bool = Field(default=True, description="Incluir using statements")
    
    templates_path: str = Field(default="./templates", description="Ruta de templates")
    custom_templates_path: Optional[str] = Field(default=None, description="Ruta de templates personalizados")
    
    code_style_indent_size: int = Field(default=4, description="Tamaño de indentación")
    code_style_use_tabs: bool = Field(default=False, description="Usar tabs")
    code_style_line_length: int = Field(default=120, description="Longitud de línea")
    
    validation_compile_check: bool = Field(default=True, description="Verificar compilación")
    validation_test_run: bool = Field(default=True, description="Ejecutar pruebas")
    validation_lint_check: bool = Field(default=True, description="Verificar linting")


class AgentConfig(BaseModel):
    """Configuración del agente"""
    name: str = Field(default="IA Agent Unit Tests", description="Nombre del agente")
    version: str = Field(default="1.0.0", description="Versión del agente")
    mode: str = Field(default="single-agent", description="Modo del agente")
    debug: bool = Field(default=False, description="Modo debug")
    log_level: str = Field(default="INFO", description="Nivel de logging")


class MultiAgentConfig(BaseModel):
    """Configuración multi-agente"""
    mode: str = Field(default="collaborative", description="Modo multi-agente")
    coordination_strategy: str = Field(default="group_chat", description="Estrategia de coordinación")
    
    agents: list = Field(default=[
        {"name": "analysis_agent", "role": "Analista", "enabled": True, "priority": 1},
        {"name": "generation_agent", "role": "Generador", "enabled": True, "priority": 2},
        {"name": "validation_agent", "role": "Validador", "enabled": True, "priority": 3},
        {"name": "optimization_agent", "role": "Optimizador", "enabled": True, "priority": 4},
        {"name": "coordinator_agent", "role": "Coordinador", "enabled": True, "priority": 0}
    ], description="Configuración de agentes")
    
    communication_group_chat_enabled: bool = Field(default=True, description="GroupChat habilitado")
    communication_agent_chat_enabled: bool = Field(default=True, description="AgentChat habilitado")
    communication_max_rounds: int = Field(default=10, description="Máximo de rondas")
    
    shared_memory_enabled: bool = Field(default=True, description="Memoria compartida habilitada")
    shared_memory_storage_path: str = Field(default="./memory/shared", description="Ruta de memoria compartida")
    shared_memory_sync_interval: int = Field(default=30, description="Intervalo de sincronización")


class Config(BaseSettings):
    """Configuración principal del sistema"""
    agent: AgentConfig = Field(default_factory=AgentConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    testing: TestingConfig = Field(default_factory=TestingConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    multi_agent: MultiAgentConfig = Field(default_factory=MultiAgentConfig)
    
    # Campos adicionales para compatibilidad con YAML
    tools: Optional[Dict[str, Any]] = Field(default=None)
    logging: Optional[Dict[str, Any]] = Field(default=None)
    performance: Optional[Dict[str, Any]] = Field(default=None)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Permitir campos extra


class ConfigManager:
    """Gestor de configuración del sistema"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/agent_configs/default.yaml"
        self._config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """Cargar configuración desde archivo YAML"""
        if self._config is not None:
            return self._config
        
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Crear configuración desde datos YAML
            self._config = Config(**config_data)
        else:
            # Usar configuración por defecto
            self._config = Config()
        
        return self._config
    
    def save_config(self, config: Config, path: Optional[str] = None) -> None:
        """Guardar configuración en archivo YAML"""
        save_path = path or self.config_path
        config_file = Path(save_path)
        
        # Crear directorio si no existe
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir a diccionario y guardar
        config_dict = config.model_dump()
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
    
    def get_config(self) -> Config:
        """Obtener configuración actual"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Actualizar configuración"""
        if self._config is None:
            self._config = Config()
        
        # Actualizar campos específicos
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def reload_config(self) -> Config:
        """Recargar configuración desde archivo"""
        self._config = None
        return self.load_config()


# Instancia global del gestor de configuración
config_manager = ConfigManager()


def get_config() -> Config:
    """Obtener configuración actual del sistema"""
    return config_manager.get_config()


def load_config(config_path: str) -> Config:
    """Cargar configuración desde archivo específico"""
    manager = ConfigManager(config_path)
    return manager.load_config()


def save_config(config: Config, path: str) -> None:
    """Guardar configuración en archivo específico"""
    manager = ConfigManager(path)
    manager.save_config(config, path)
