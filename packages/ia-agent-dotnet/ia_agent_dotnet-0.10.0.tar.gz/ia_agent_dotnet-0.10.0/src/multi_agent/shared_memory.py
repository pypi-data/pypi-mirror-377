"""
Memoria compartida para sistema multi-agente
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
import json
import threading
from pathlib import Path

import chromadb
from chromadb.config import Settings

from utils.helpers import file_helper, json_helper
from utils.logging import get_logger

logger = get_logger("shared-memory")


@dataclass
class SharedEntry:
    """Entrada en memoria compartida"""
    id: str
    agent_name: str
    content: str
    entry_type: str  # 'conversation', 'project_context', 'learned_pattern', 'user_preference'
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class SharedContext:
    """Contexto compartido del proyecto"""
    project_id: str
    project_name: str
    project_path: str
    framework: str
    patterns: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


class SharedMemory:
    """Memoria compartida entre agentes"""
    
    def __init__(self, storage_path: str = "./memory/shared"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logger
        self.lock = threading.Lock()
        
        # Configurar ChromaDB para memoria compartida
        self._setup_chromadb()
        
        # Contexto del proyecto actual
        self.current_context: Optional[SharedContext] = None
        
        # Cache de entradas frecuentemente accedidas
        self.access_cache: Dict[str, SharedEntry] = {}
    
    def _setup_chromadb(self):
        """Configurar ChromaDB para memoria compartida"""
        try:
            # Usar singleton para evitar conflictos
            from utils.chromadb_singleton import chromadb_singleton
            
            self.chroma_client = chromadb_singleton.get_client("shared_memory", self.storage_path)
            
            # Si el cliente es None, usar modo sin persistencia
            if self.chroma_client is None:
                self.logger.warning("ChromaDB no disponible para memoria compartida, usando modo sin persistencia")
                self.collections = {}
                return
            
            # Colecciones para diferentes tipos de memoria
            self.collections = {}
            
            collection_configs = {
                'conversations': 'Conversaciones entre agentes',
                'project_context': 'Contexto de proyectos',
                'learned_patterns': 'Patrones aprendidos',
                'user_preferences': 'Preferencias del usuario'
            }
            
            for collection_name, description in collection_configs.items():
                try:
                    self.collections[collection_name] = self.chroma_client.get_collection(collection_name)
                    self.logger.info(f"Colección existente cargada: {collection_name}")
                except Exception:
                    self.collections[collection_name] = self.chroma_client.create_collection(
                        name=collection_name,
                        metadata={"description": description}
                    )
                    self.logger.info(f"Nueva colección creada: {collection_name}")
            
        except Exception as e:
            self.logger.error(f"Error al configurar ChromaDB compartido: {e}")
            raise
    
    def add_entry(self, agent_name: str, content: str, entry_type: str, 
                  metadata: Optional[Dict[str, Any]] = None, entry_id: Optional[str] = None) -> str:
        """Agregar entrada a memoria compartida"""
        try:
            with self.lock:
                # Generar ID si no se proporciona
                if not entry_id:
                    entry_id = f"shared_{entry_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                
                # Crear entrada
                entry = SharedEntry(
                    id=entry_id,
                    agent_name=agent_name,
                    content=content,
                    entry_type=entry_type,
                    metadata=metadata or {}
                )
                
                # Agregar a colección correspondiente
                if entry_type in self.collections:
                    collection = self.collections[entry_type]
                    
                    # Generar embedding simple (en implementación real usar modelo de embeddings)
                    embedding = self._generate_simple_embedding(content)
                    
                    # Preparar metadatos
                    entry_metadata = {
                        'agent_name': agent_name,
                        'timestamp': entry.timestamp.isoformat()
                    }
                    if metadata:
                        entry_metadata.update(metadata)
                    
                    collection.add(
                        ids=[entry_id],
                        documents=[content],
                        embeddings=[embedding],
                        metadatas=[entry_metadata]
                    )
                
                # Guardar en archivo JSON para persistencia
                self._save_entry_to_file(entry)
                
                # Agregar al cache
                self.access_cache[entry_id] = entry
                
                self.logger.debug(f"Entrada agregada a memoria compartida: {entry_id}")
                return entry_id
                
        except Exception as e:
            self.logger.error(f"Error al agregar entrada compartida: {e}")
            raise
    
    def get_entry(self, entry_id: str) -> Optional[SharedEntry]:
        """Obtener entrada por ID"""
        try:
            with self.lock:
                # Verificar cache primero
                if entry_id in self.access_cache:
                    entry = self.access_cache[entry_id]
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                    return entry
                
                # Buscar en archivos
                entry = self._load_entry_from_file(entry_id)
                if entry:
                    # Agregar al cache
                    self.access_cache[entry_id] = entry
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                
                return entry
                
        except Exception as e:
            self.logger.error(f"Error al obtener entrada {entry_id}: {e}")
            return None
    
    def search_entries(self, query: str, entry_type: Optional[str] = None, 
                      limit: int = 10) -> List[SharedEntry]:
        """Buscar entradas en memoria compartida"""
        try:
            with self.lock:
                results = []
                
                # Buscar en colecciones específicas o todas
                collections_to_search = [entry_type] if entry_type else list(self.collections.keys())
                
                for collection_name in collections_to_search:
                    if collection_name in self.collections:
                        collection = self.collections[collection_name]
                        
                        # Generar embedding de consulta
                        query_embedding = self._generate_simple_embedding(query)
                        
                        # Buscar en ChromaDB
                        search_results = collection.query(
                            query_embeddings=[query_embedding],
                            n_results=limit,
                            include=['documents', 'metadatas', 'distances']
                        )
                        
                        # Procesar resultados
                        if search_results['ids'] and search_results['ids'][0]:
                            for i, entry_id in enumerate(search_results['ids'][0]):
                                content = search_results['documents'][0][i]
                                metadata = search_results['metadatas'][0][i]
                                distance = search_results['distances'][0][i]
                                
                                entry = SharedEntry(
                                    id=entry_id,
                                    agent_name=metadata.get('agent_name', 'unknown'),
                                    content=content,
                                    entry_type=collection_name,
                                    metadata=metadata
                                )
                                
                                results.append(entry)
                
                # Ordenar por relevancia (distancia)
                results.sort(key=lambda x: x.metadata.get('distance', 1.0))
                
                return results[:limit]
                
        except Exception as e:
            self.logger.error(f"Error en búsqueda compartida: {e}")
            return []
    
    def set_project_context(self, project_id: str, project_name: str, 
                           project_path: str, framework: str) -> bool:
        """Establecer contexto del proyecto actual"""
        try:
            with self.lock:
                self.current_context = SharedContext(
                    project_id=project_id,
                    project_name=project_name,
                    project_path=project_path,
                    framework=framework
                )
                
                # Guardar contexto
                self._save_project_context()
                
                self.logger.info(f"Contexto de proyecto establecido: {project_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error al establecer contexto de proyecto: {e}")
            return False
    
    def get_project_context(self) -> Optional[SharedContext]:
        """Obtener contexto del proyecto actual"""
        return self.current_context
    
    def update_project_context(self, **kwargs) -> bool:
        """Actualizar contexto del proyecto"""
        try:
            with self.lock:
                if not self.current_context:
                    return False
                
                # Actualizar campos
                for key, value in kwargs.items():
                    if hasattr(self.current_context, key):
                        setattr(self.current_context, key, value)
                
                self.current_context.last_updated = datetime.now()
                
                # Guardar contexto actualizado
                self._save_project_context()
                
                self.logger.debug("Contexto de proyecto actualizado")
                return True
                
        except Exception as e:
            self.logger.error(f"Error al actualizar contexto de proyecto: {e}")
            return False
    
    def add_learned_pattern(self, agent_name: str, pattern: str, 
                           pattern_type: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Agregar patrón aprendido"""
        return self.add_entry(
            agent_name=agent_name,
            content=pattern,
            entry_type='learned_patterns',
            metadata={
                'pattern_type': pattern_type,
                **(metadata or {})
            }
        )
    
    def get_learned_patterns(self, pattern_type: Optional[str] = None) -> List[SharedEntry]:
        """Obtener patrones aprendidos"""
        if pattern_type:
            return self.search_entries(f"pattern_type:{pattern_type}", 'learned_patterns')
        return self.search_entries("", 'learned_patterns')
    
    def add_user_preference(self, agent_name: str, preference_key: str, 
                           preference_value: Any) -> str:
        """Agregar preferencia del usuario"""
        return self.add_entry(
            agent_name=agent_name,
            content=str(preference_value),
            entry_type='user_preferences',
            metadata={'preference_key': preference_key}
        )
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Obtener preferencias del usuario"""
        preferences = {}
        entries = self.search_entries("", 'user_preferences')
        
        for entry in entries:
            preference_key = entry.metadata.get('preference_key')
            if preference_key:
                preferences[preference_key] = entry.content
        
        return preferences
    
    def sync_agent_memory(self, agent_name: str, memory_data: Dict[str, Any]) -> bool:
        """Sincronizar memoria de un agente con memoria compartida"""
        try:
            with self.lock:
                # Agregar datos de memoria del agente
                for key, value in memory_data.items():
                    self.add_entry(
                        agent_name=agent_name,
                        content=str(value),
                        entry_type='conversations',
                        metadata={'memory_key': key}
                    )
                
                self.logger.info(f"Memoria sincronizada para agente: {agent_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error al sincronizar memoria del agente {agent_name}: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de memoria compartida"""
        try:
            stats = {
                'total_entries': 0,
                'entries_by_type': {},
                'cache_size': len(self.access_cache),
                'project_context': self.current_context is not None
            }
            
            # Contar entradas por tipo
            for collection_name, collection in self.collections.items():
                count = collection.count()
                stats['entries_by_type'][collection_name] = count
                stats['total_entries'] += count
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas: {e}")
            return {}
    
    def clear_memory(self, entry_type: Optional[str] = None) -> bool:
        """Limpiar memoria compartida"""
        try:
            with self.lock:
                if entry_type:
                    # Limpiar tipo específico
                    if entry_type in self.collections:
                        self.chroma_client.delete_collection(entry_type)
                        self.collections[entry_type] = self.chroma_client.create_collection(
                            name=entry_type,
                            metadata={"description": f"Memoria compartida - {entry_type}"}
                        )
                else:
                    # Limpiar toda la memoria
                    for collection_name in list(self.collections.keys()):
                        self.chroma_client.delete_collection(collection_name)
                        self.collections[collection_name] = self.chroma_client.create_collection(
                            name=collection_name,
                            metadata={"description": f"Memoria compartida - {collection_name}"}
                        )
                
                # Limpiar cache
                self.access_cache.clear()
                
                # Limpiar contexto
                self.current_context = None
                
                self.logger.info("Memoria compartida limpiada")
                return True
                
        except Exception as e:
            self.logger.error(f"Error al limpiar memoria: {e}")
            return False
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generar embedding simple (placeholder)"""
        # En implementación real, usar modelo de embeddings
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        return [float(b) / 255.0 for b in hash_bytes[:8]]  # Embedding de 8 dimensiones
    
    def _save_entry_to_file(self, entry: SharedEntry):
        """Guardar entrada en archivo JSON"""
        try:
            entry_file = self.storage_path / f"entry_{entry.id}.json"
            
            entry_data = {
                'id': entry.id,
                'agent_name': entry.agent_name,
                'content': entry.content,
                'entry_type': entry.entry_type,
                'metadata': entry.metadata,
                'timestamp': entry.timestamp.isoformat(),
                'access_count': entry.access_count,
                'last_accessed': entry.last_accessed.isoformat() if entry.last_accessed else None
            }
            
            json_helper.save_json(entry_data, entry_file)
            
        except Exception as e:
            self.logger.error(f"Error al guardar entrada en archivo: {e}")
    
    def _load_entry_from_file(self, entry_id: str) -> Optional[SharedEntry]:
        """Cargar entrada desde archivo JSON"""
        try:
            entry_file = self.storage_path / f"entry_{entry_id}.json"
            
            if not entry_file.exists():
                return None
            
            entry_data = json_helper.load_json(entry_file)
            
            return SharedEntry(
                id=entry_data['id'],
                agent_name=entry_data['agent_name'],
                content=entry_data['content'],
                entry_type=entry_data['entry_type'],
                metadata=entry_data['metadata'],
                timestamp=datetime.fromisoformat(entry_data['timestamp']),
                access_count=entry_data.get('access_count', 0),
                last_accessed=datetime.fromisoformat(entry_data['last_accessed']) if entry_data.get('last_accessed') else None
            )
            
        except Exception as e:
            self.logger.error(f"Error al cargar entrada desde archivo: {e}")
            return None
    
    def _save_project_context(self):
        """Guardar contexto del proyecto"""
        try:
            if not self.current_context:
                return
            
            context_file = self.storage_path / "project_context.json"
            
            context_data = {
                'project_id': self.current_context.project_id,
                'project_name': self.current_context.project_name,
                'project_path': self.current_context.project_path,
                'framework': self.current_context.framework,
                'patterns': self.current_context.patterns,
                'user_preferences': self.current_context.user_preferences,
                'last_updated': self.current_context.last_updated.isoformat()
            }
            
            json_helper.save_json(context_data, context_file)
            
        except Exception as e:
            self.logger.error(f"Error al guardar contexto de proyecto: {e}")
    
    def _load_project_context(self) -> Optional[SharedContext]:
        """Cargar contexto del proyecto"""
        try:
            context_file = self.storage_path / "project_context.json"
            
            if not context_file.exists():
                return None
            
            context_data = json_helper.load_json(context_file)
            
            return SharedContext(
                project_id=context_data['project_id'],
                project_name=context_data['project_name'],
                project_path=context_data['project_path'],
                framework=context_data['framework'],
                patterns=context_data.get('patterns', []),
                user_preferences=context_data.get('user_preferences', {}),
                last_updated=datetime.fromisoformat(context_data['last_updated'])
            )
            
        except Exception as e:
            self.logger.error(f"Error al cargar contexto de proyecto: {e}")
            return None
