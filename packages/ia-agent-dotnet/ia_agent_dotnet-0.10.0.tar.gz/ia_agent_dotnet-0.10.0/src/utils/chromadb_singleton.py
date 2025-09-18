"""
Singleton para ChromaDB para evitar conflictos de múltiples instancias
IA Agent para Generación de Pruebas Unitarias .NET
"""

import os
import threading
import uuid
from typing import Optional, Dict, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings

from utils.logging import get_logger

logger = get_logger("chromadb-singleton")


class ChromaDBSingleton:
    """Singleton para ChromaDB"""
    
    _instance: Optional['ChromaDBSingleton'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'ChromaDBSingleton':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._clients: Dict[str, chromadb.Client] = {}
            self._initialized = True
    
    def get_client(self, agent_name: str, base_path: Optional[Path] = None) -> chromadb.Client:
        """Obtener cliente ChromaDB compartido para todos los agentes"""
        # Usar una sola instancia compartida para todos los agentes
        client_key = "shared_chromadb_client"
        
        # Si ya tenemos un cliente compartido, reutilizarlo
        if client_key in self._clients:
            logger.info(f"Reutilizando cliente ChromaDB compartido para agente: {agent_name}")
            return self._clients[client_key]
        
        try:
            if base_path is None:
                base_path = Path("./memory/vector")
            
            # Crear path compartido
            shared_path = base_path / "shared"
            shared_path.mkdir(parents=True, exist_ok=True)
            
            # Configuración compartida
            settings = Settings(
                persist_directory=str(shared_path),
                anonymized_telemetry=False
            )
            
            # Crear cliente compartido
            client = chromadb.Client(settings)
            self._clients[client_key] = client
            
            logger.info(f"Cliente ChromaDB compartido creado para agente: {agent_name}")
            return client
            
        except Exception as e:
            logger.warning(f"Error al crear cliente ChromaDB compartido para {agent_name}: {e}")
            # Fallback: usar cliente en memoria sin persistencia
            try:
                client = chromadb.Client()
                self._clients[client_key] = client
                logger.warning(f"Usando cliente ChromaDB en memoria compartido para {agent_name}")
                return client
            except Exception as e2:
                logger.error(f"Error crítico al crear cliente en memoria: {e2}")
                # Último recurso: retornar None y manejar en el código que lo usa
                return None
    
    def reset(self):
        """Resetear el singleton (para pruebas)"""
        with self._lock:
            self._clients.clear()


# Instancia global
chromadb_singleton = ChromaDBSingleton()
