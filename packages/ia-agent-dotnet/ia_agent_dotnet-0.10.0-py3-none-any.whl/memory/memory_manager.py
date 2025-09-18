#!/usr/bin/env python3
"""
Manager de memoria optimizado
IA Agent para Generación de Pruebas Unitarias .NET
"""

import asyncio
import threading
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import OrderedDict
import logging

from langchain_agents.memory.vector_memory import VectorMemory
from multi_agent.shared_memory import SharedMemory
from config.environment import environment_manager


class MemoryCache:
    """Cache de memoria con LRU (Least Recently Used)"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Obtener elemento del cache"""
        with self.lock:
            if key in self.cache:
                # Mover al final (más reciente)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.hits += 1
                return value
            self.misses += 1
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Agregar elemento al cache"""
        with self.lock:
            if key in self.cache:
                # Actualizar existente
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Eliminar el menos reciente
                self.cache.popitem(last=False)
            
            self.cache[key] = value
    
    def clear(self) -> None:
        """Limpiar cache"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }


class MemoryManager:
    """Manager centralizado de memoria"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = environment_manager.get_config()
        
        # Cache de memoria
        self.cache = MemoryCache(self.config.memory_cache_size)
        
        # Instancias de memoria por agente
        self.agent_memories: Dict[str, VectorMemory] = {}
        self.shared_memory: Optional[SharedMemory] = None
        
        # Lock para operaciones concurrentes
        self.lock = threading.RLock()
        
        # Estadísticas
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "memory_operations": 0,
            "last_cleanup": time.time()
        }
        
        self._initialize_memories()
    
    def _initialize_memories(self):
        """Inicializar memorias de agentes"""
        try:
            # Memoria compartida
            self.shared_memory = SharedMemory()
            self.logger.info("Memoria compartida inicializada")
            
            # Memorias de agentes (lazy loading)
            self.logger.info("Sistema de memoria inicializado")
            
        except Exception as e:
            self.logger.error(f"Error al inicializar memorias: {e}")
    
    def get_agent_memory(self, agent_name: str) -> VectorMemory:
        """Obtener memoria de agente (lazy loading)"""
        with self.lock:
            if agent_name not in self.agent_memories:
                try:
                    self.agent_memories[agent_name] = VectorMemory(
                        agent_name=agent_name,
                        storage_path=Path(self.config.chromadb_persist_directory)
                    )
                    self.logger.info(f"Memoria del agente {agent_name} inicializada")
                except Exception as e:
                    self.logger.error(f"Error al inicializar memoria del agente {agent_name}: {e}")
                    # Crear memoria temporal
                    self.agent_memories[agent_name] = VectorMemory(
                        agent_name=agent_name,
                        storage_path=None
                    )
            
            return self.agent_memories[agent_name]
    
    def get_shared_memory(self) -> Optional[SharedMemory]:
        """Obtener memoria compartida"""
        return self.shared_memory
    
    def add_to_cache(self, key: str, value: Any) -> None:
        """Agregar al cache"""
        self.cache.put(key, value)
        self.stats["cache_hits"] += 1
    
    def get_from_cache(self, key: str) -> Optional[Any]:
        """Obtener del cache"""
        value = self.cache.get(key)
        if value is not None:
            self.stats["cache_hits"] += 1
        else:
            self.stats["cache_misses"] += 1
        return value
    
    def search_memory(self, agent_name: str, query: str, limit: int = 5) -> List[Any]:
        """Buscar en memoria con cache"""
        cache_key = f"search_{agent_name}_{hash(query)}_{limit}"
        
        # Intentar obtener del cache
        cached_result = self.get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Buscar en memoria
        try:
            memory = self.get_agent_memory(agent_name)
            results = memory.search(query, limit=limit)
            
            # Guardar en cache
            self.add_to_cache(cache_key, results)
            self.stats["memory_operations"] += 1
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda de memoria: {e}")
            return []
    
    def add_to_memory(self, agent_name: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Agregar a memoria"""
        try:
            memory = self.get_agent_memory(agent_name)
            entry_id = memory.add_entry(content, metadata)
            self.stats["memory_operations"] += 1
            
            # Limpiar cache relacionado
            self._clear_agent_cache(agent_name)
            
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Error al agregar a memoria: {e}")
            return ""
    
    def _clear_agent_cache(self, agent_name: str):
        """Limpiar cache de un agente específico"""
        keys_to_remove = [
            key for key in self.cache.cache.keys() 
            if key.startswith(f"search_{agent_name}_")
        ]
        
        for key in keys_to_remove:
            self.cache.cache.pop(key, None)
    
    def cleanup_memory(self) -> None:
        """Limpiar memoria y optimizar"""
        current_time = time.time()
        
        # Limpiar cache si es necesario
        if current_time - self.stats["last_cleanup"] > 3600:  # 1 hora
            self.cache.clear()
            self.stats["last_cleanup"] = current_time
            self.logger.info("Cache de memoria limpiado")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de memoria"""
        cache_stats = self.cache.get_stats()
        
        return {
            "cache": cache_stats,
            "agent_memories": len(self.agent_memories),
            "shared_memory": self.shared_memory is not None,
            "stats": self.stats.copy(),
            "config": {
                "cache_size": self.config.memory_cache_size,
                "persist_directory": self.config.chromadb_persist_directory
            }
        }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Optimizar memoria"""
        optimization_results = {
            "cache_cleared": False,
            "memory_cleaned": False,
            "stats_reset": False
        }
        
        try:
            # Limpiar cache
            old_size = len(self.cache.cache)
            self.cache.clear()
            optimization_results["cache_cleared"] = True
            
            # Limpiar estadísticas
            self.stats = {
                "cache_hits": 0,
                "cache_misses": 0,
                "memory_operations": 0,
                "last_cleanup": time.time()
            }
            optimization_results["stats_reset"] = True
            
            self.logger.info(f"Memoria optimizada. Cache limpiado: {old_size} elementos")
            
        except Exception as e:
            self.logger.error(f"Error en optimización de memoria: {e}")
        
        return optimization_results
    
    def shutdown(self) -> None:
        """Cerrar manager de memoria"""
        try:
            # Limpiar cache
            self.cache.clear()
            
            # Cerrar memorias
            for memory in self.agent_memories.values():
                if hasattr(memory, 'close'):
                    memory.close()
            
            if self.shared_memory and hasattr(self.shared_memory, 'close'):
                self.shared_memory.close()
            
            self.logger.info("Memory manager cerrado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al cerrar memory manager: {e}")


# Instancia global del manager de memoria
memory_manager = MemoryManager()
