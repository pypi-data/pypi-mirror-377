"""
Memoria vectorial para búsqueda semántica
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import json
import os
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

from utils.helpers import file_helper, json_helper
from utils.logging import get_logger
from utils.chromadb_singleton import chromadb_singleton

logger = get_logger("vector-memory")


@dataclass
class VectorEntry:
    """Entrada en memoria vectorial"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    """Resultado de búsqueda vectorial"""
    entry: VectorEntry
    similarity: float
    distance: float


class VectorMemory:
    """Memoria vectorial para búsqueda semántica"""
    
    def __init__(self, agent_name: str, storage_path: str = "./memory/individual", 
                 collection_name: Optional[str] = None):
        self.agent_name = agent_name
        self.storage_path = Path(storage_path) / agent_name / "vector"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name or f"{agent_name}_memory"
        self.logger = logger
        
        # Configurar modelo de embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Configurar ChromaDB
        self._setup_chromadb()
        
        # Cache de embeddings
        self.embedding_cache: Dict[str, List[float]] = {}
    
    def _setup_chromadb(self):
        """Configurar ChromaDB usando singleton"""
        try:
            # Usar singleton para evitar conflictos
            self.chroma_client = chromadb_singleton.get_client(self.agent_name, self.storage_path)
            
            # Si el cliente es None, usar modo sin persistencia
            if self.chroma_client is None:
                self.logger.warning("ChromaDB no disponible, usando modo sin persistencia")
                self.collection = None
                return
            
            # Obtener o crear colección
            try:
                self.collection = self.chroma_client.get_collection(self.collection_name)
                self.logger.info(f"Colección existente cargada: {self.collection_name}")
            except Exception:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"agent": self.agent_name}
                )
                self.logger.info(f"Nueva colección creada: {self.collection_name}")
            
        except Exception as e:
            self.logger.error(f"Error al configurar ChromaDB: {e}")
            self.logger.warning("Usando modo sin persistencia")
            self.chroma_client = None
            self.collection = None
    
    def add_entry(self, content: str, metadata: Optional[Dict[str, Any]] = None, 
                  entry_id: Optional[str] = None) -> str:
        """Agregar entrada a la memoria vectorial"""
        try:
            # Generar ID si no se proporciona
            if not entry_id:
                entry_id = f"{self.agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Generar embedding
            embedding = self._generate_embedding(content)
            
            # Crear entrada
            entry = VectorEntry(
                id=entry_id,
                content=content,
                metadata=metadata or {},
                embedding=embedding
            )
            
            # Agregar a ChromaDB si está disponible
            if self.collection is not None:
                self.collection.add(
                    ids=[entry_id],
                    documents=[content],
                    embeddings=[embedding],
                    metadatas=[metadata or {}]
                )
            
            # Agregar al cache
            self.embedding_cache[entry_id] = embedding
            
            self.logger.debug(f"Entrada agregada a memoria vectorial: {entry_id}")
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Error al agregar entrada: {e}")
            raise
    
    def search(self, query: str, limit: int = 5, 
               similarity_threshold: float = 0.7) -> List[SearchResult]:
        """Buscar entradas similares"""
        try:
            # Si no hay colección disponible, retornar lista vacía
            if self.collection is None:
                self.logger.warning("ChromaDB no disponible, búsqueda no posible")
                return []
            
            # Generar embedding de la consulta
            query_embedding = self._generate_embedding(query)
            
            # Buscar en ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Procesar resultados
            search_results = []
            
            if results['ids'] and results['ids'][0]:
                for i, entry_id in enumerate(results['ids'][0]):
                    content = results['documents'][0][i]
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Convertir distancia a similitud (ChromaDB usa distancia coseno)
                    similarity = 1 - distance
                    
                    if similarity >= similarity_threshold:
                        entry = VectorEntry(
                            id=entry_id,
                            content=content,
                            metadata=metadata,
                            embedding=None  # No incluir embedding en resultado
                        )
                        
                        search_result = SearchResult(
                            entry=entry,
                            similarity=similarity,
                            distance=distance
                        )
                        
                        search_results.append(search_result)
            
            self.logger.debug(f"Búsqueda completada: {len(search_results)} resultados")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda vectorial: {e}")
            raise
    
    def get_entry(self, entry_id: str) -> Optional[VectorEntry]:
        """Obtener entrada por ID"""
        try:
            results = self.collection.get(
                ids=[entry_id],
                include=['documents', 'metadatas']
            )
            
            if results['ids'] and results['ids'][0]:
                content = results['documents'][0][0]
                metadata = results['metadatas'][0][0]
                
                return VectorEntry(
                    id=entry_id,
                    content=content,
                    metadata=metadata
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error al obtener entrada {entry_id}: {e}")
            return None
    
    def update_entry(self, entry_id: str, content: Optional[str] = None, 
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Actualizar entrada existente"""
        try:
            # Obtener entrada actual
            current_entry = self.get_entry(entry_id)
            if not current_entry:
                return False
            
            # Actualizar campos
            new_content = content if content is not None else current_entry.content
            new_metadata = metadata if metadata is not None else current_entry.metadata
            
            # Generar nuevo embedding si el contenido cambió
            new_embedding = None
            if content is not None and content != current_entry.content:
                new_embedding = self._generate_embedding(new_content)
            
            # Actualizar en ChromaDB
            self.collection.update(
                ids=[entry_id],
                documents=[new_content] if new_content else None,
                embeddings=[new_embedding] if new_embedding else None,
                metadatas=[new_metadata]
            )
            
            # Actualizar cache
            if new_embedding:
                self.embedding_cache[entry_id] = new_embedding
            
            self.logger.debug(f"Entrada actualizada: {entry_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al actualizar entrada {entry_id}: {e}")
            return False
    
    def delete_entry(self, entry_id: str) -> bool:
        """Eliminar entrada"""
        try:
            self.collection.delete(ids=[entry_id])
            
            # Remover del cache
            if entry_id in self.embedding_cache:
                del self.embedding_cache[entry_id]
            
            self.logger.debug(f"Entrada eliminada: {entry_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al eliminar entrada {entry_id}: {e}")
            return False
    
    def get_all_entries(self, limit: Optional[int] = None) -> List[VectorEntry]:
        """Obtener todas las entradas"""
        try:
            results = self.collection.get(
                include=['documents', 'metadatas'],
                limit=limit
            )
            
            entries = []
            if results['ids']:
                for i, entry_id in enumerate(results['ids']):
                    content = results['documents'][i]
                    metadata = results['metadatas'][i]
                    
                    entry = VectorEntry(
                        id=entry_id,
                        content=content,
                        metadata=metadata
                    )
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            self.logger.error(f"Error al obtener todas las entradas: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la colección"""
        try:
            count = self.collection.count()
            
            return {
                'collection_name': self.collection_name,
                'agent_name': self.agent_name,
                'total_entries': count,
                'cache_size': len(self.embedding_cache),
                'storage_path': str(self.storage_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas: {e}")
            return {}
    
    def clear_memory(self) -> bool:
        """Limpiar toda la memoria"""
        try:
            # Eliminar colección
            self.chroma_client.delete_collection(self.collection_name)
            
            # Recrear colección vacía
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"agent": self.agent_name}
            )
            
            # Limpiar cache
            self.embedding_cache.clear()
            
            self.logger.info("Memoria vectorial limpiada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al limpiar memoria: {e}")
            return False
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generar embedding para texto"""
        try:
            # Verificar cache
            text_hash = hash(text)
            if text_hash in self.embedding_cache:
                return self.embedding_cache[text_hash]
            
            # Generar embedding
            embedding = self.embedding_model.encode(text).tolist()
            
            # Agregar al cache
            self.embedding_cache[text_hash] = embedding
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Error al generar embedding: {e}")
            raise
    
    def save_cache(self) -> bool:
        """Guardar cache de embeddings"""
        try:
            cache_file = self.storage_path / "embedding_cache.json"
            
            # Convertir cache a formato serializable
            cache_data = {
                str(k): v for k, v in self.embedding_cache.items()
            }
            
            json_helper.save_json(cache_data, cache_file)
            self.logger.debug("Cache de embeddings guardado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar cache: {e}")
            return False
    
    def load_cache(self) -> bool:
        """Cargar cache de embeddings"""
        try:
            cache_file = self.storage_path / "embedding_cache.json"
            
            if not cache_file.exists():
                return True
            
            cache_data = json_helper.load_json(cache_file)
            
            # Restaurar cache
            self.embedding_cache = {
                int(k) if k.isdigit() else k: v 
                for k, v in cache_data.items()
            }
            
            self.logger.debug("Cache de embeddings cargado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al cargar cache: {e}")
            return False
