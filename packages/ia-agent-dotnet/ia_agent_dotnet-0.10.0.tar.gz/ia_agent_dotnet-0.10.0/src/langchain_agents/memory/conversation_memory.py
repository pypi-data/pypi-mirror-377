"""
Memoria de conversación para agentes individuales
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
import json
from pathlib import Path

from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage

from utils.helpers import file_helper, json_helper
from utils.logging import get_logger

logger = get_logger("conversation-memory")


@dataclass
class ConversationEntry:
    """Entrada de conversación"""
    timestamp: datetime
    message_type: str  # 'human', 'ai', 'system'
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Contexto de conversación"""
    session_id: str
    agent_name: str
    start_time: datetime
    last_activity: datetime
    message_count: int = 0
    context_data: Dict[str, Any] = field(default_factory=dict)


class ConversationMemory:
    """Memoria de conversación para agentes individuales"""
    
    def __init__(self, agent_name: str, storage_path: str = "./memory/individual"):
        self.agent_name = agent_name
        self.storage_path = Path(storage_path) / agent_name
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logger
        self.current_context: Optional[ConversationContext] = None
        self.conversation_history: List[ConversationEntry] = []
        
        # Configurar memoria de LangChain
        self._setup_langchain_memory()
    
    def _setup_langchain_memory(self):
        """Configurar memoria de LangChain"""
        try:
            # Archivo para historial de mensajes
            chat_file = self.storage_path / "chat_history.json"
            
            # Memoria de buffer
            self.buffer_memory = ConversationBufferMemory(
                chat_memory=FileChatMessageHistory(str(chat_file)),
                return_messages=True,
                memory_key="chat_history"
            )
            
            # Memoria de resumen (solo buffer por ahora)
            # self.summary_memory = ConversationSummaryMemory(
            #     llm=None,  # Se configurará cuando se tenga el LLM
            #     chat_memory=FileChatMessageHistory(str(chat_file)),
            #     return_messages=True,
            #     memory_key="summary_history"
            # )
            self.summary_memory = None  # Se configurará más tarde cuando tengamos LLM
            
            self.logger.info(f"Memoria de LangChain configurada para {self.agent_name}")
            
        except Exception as e:
            self.logger.error(f"Error al configurar memoria de LangChain: {e}")
            raise
    
    def start_conversation(self, session_id: str, context_data: Optional[Dict[str, Any]] = None) -> bool:
        """Iniciar nueva conversación"""
        try:
            self.current_context = ConversationContext(
                session_id=session_id,
                agent_name=self.agent_name,
                start_time=datetime.now(),
                last_activity=datetime.now(),
                context_data=context_data or {}
            )
            
            self.conversation_history.clear()
            
            # Agregar mensaje de sistema
            self.add_message("system", f"Conversación iniciada con {self.agent_name}")
            
            self.logger.info(f"Conversación iniciada: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al iniciar conversación: {e}")
            return False
    
    def add_message(self, message_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Agregar mensaje a la conversación"""
        try:
            if not self.current_context:
                self.logger.warning("No hay conversación activa")
                return False
            
            entry = ConversationEntry(
                timestamp=datetime.now(),
                message_type=message_type,
                content=content,
                metadata=metadata or {}
            )
            
            self.conversation_history.append(entry)
            self.current_context.message_count += 1
            self.current_context.last_activity = datetime.now()
            
            # Agregar a memoria de LangChain
            self._add_to_langchain_memory(message_type, content)
            
            self.logger.debug(f"Mensaje agregado: {message_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al agregar mensaje: {e}")
            return False
    
    def _add_to_langchain_memory(self, message_type: str, content: str):
        """Agregar mensaje a memoria de LangChain"""
        try:
            if message_type == "human":
                self.buffer_memory.chat_memory.add_user_message(content)
            elif message_type == "ai":
                self.buffer_memory.chat_memory.add_ai_message(content)
            elif message_type == "system":
                self.buffer_memory.chat_memory.add_message(SystemMessage(content=content))
            
        except Exception as e:
            self.logger.error(f"Error al agregar a memoria de LangChain: {e}")
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[ConversationEntry]:
        """Obtener historial de conversación"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history.copy()
    
    def get_langchain_memory(self, memory_type: str = "buffer") -> Union[ConversationBufferMemory, ConversationSummaryMemory]:
        """Obtener memoria de LangChain"""
        if memory_type == "summary" and self.summary_memory is not None:
            return self.summary_memory
        return self.buffer_memory
    
    def get_context(self) -> Optional[ConversationContext]:
        """Obtener contexto actual"""
        return self.current_context
    
    def update_context(self, context_data: Dict[str, Any]) -> bool:
        """Actualizar contexto de conversación"""
        try:
            if not self.current_context:
                return False
            
            self.current_context.context_data.update(context_data)
            self.current_context.last_activity = datetime.now()
            
            self.logger.debug("Contexto actualizado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al actualizar contexto: {e}")
            return False
    
    def save_conversation(self) -> bool:
        """Guardar conversación en archivo"""
        try:
            if not self.current_context:
                return False
            
            # Preparar datos para guardar
            conversation_data = {
                'context': {
                    'session_id': self.current_context.session_id,
                    'agent_name': self.current_context.agent_name,
                    'start_time': self.current_context.start_time.isoformat(),
                    'last_activity': self.current_context.last_activity.isoformat(),
                    'message_count': self.current_context.message_count,
                    'context_data': self.current_context.context_data
                },
                'history': [
                    {
                        'timestamp': entry.timestamp.isoformat(),
                        'message_type': entry.message_type,
                        'content': entry.content,
                        'metadata': entry.metadata
                    }
                    for entry in self.conversation_history
                ]
            }
            
            # Guardar archivo
            save_file = self.storage_path / f"conversation_{self.current_context.session_id}.json"
            json_helper.save_json(conversation_data, save_file)
            
            self.logger.info(f"Conversación guardada: {save_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar conversación: {e}")
            return False
    
    def load_conversation(self, session_id: str) -> bool:
        """Cargar conversación desde archivo"""
        try:
            load_file = self.storage_path / f"conversation_{session_id}.json"
            
            if not load_file.exists():
                self.logger.warning(f"Archivo de conversación no encontrado: {load_file}")
                return False
            
            # Cargar datos
            conversation_data = json_helper.load_json(load_file)
            
            # Restaurar contexto
            context_data = conversation_data['context']
            self.current_context = ConversationContext(
                session_id=context_data['session_id'],
                agent_name=context_data['agent_name'],
                start_time=datetime.fromisoformat(context_data['start_time']),
                last_activity=datetime.fromisoformat(context_data['last_activity']),
                message_count=context_data['message_count'],
                context_data=context_data['context_data']
            )
            
            # Restaurar historial
            self.conversation_history = []
            for entry_data in conversation_data['history']:
                entry = ConversationEntry(
                    timestamp=datetime.fromisoformat(entry_data['timestamp']),
                    message_type=entry_data['message_type'],
                    content=entry_data['content'],
                    metadata=entry_data['metadata']
                )
                self.conversation_history.append(entry)
            
            self.logger.info(f"Conversación cargada: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al cargar conversación: {e}")
            return False
    
    def end_conversation(self) -> bool:
        """Finalizar conversación"""
        try:
            if not self.current_context:
                return False
            
            # Guardar conversación
            self.save_conversation()
            
            # Limpiar estado
            self.current_context = None
            self.conversation_history.clear()
            
            self.logger.info("Conversación finalizada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al finalizar conversación: {e}")
            return False
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Obtener resumen de la conversación"""
        if not self.current_context:
            return {}
        
        return {
            'session_id': self.current_context.session_id,
            'agent_name': self.current_context.agent_name,
            'duration': (self.current_context.last_activity - self.current_context.start_time).total_seconds(),
            'message_count': self.current_context.message_count,
            'context_data': self.current_context.context_data,
            'last_activity': self.current_context.last_activity.isoformat()
        }
    
    def clear_memory(self) -> bool:
        """Limpiar memoria"""
        try:
            self.current_context = None
            self.conversation_history.clear()
            
            # Limpiar memoria de LangChain
            self.buffer_memory.clear()
            if self.summary_memory is not None and hasattr(self.summary_memory, 'clear'):
                self.summary_memory.clear()
            
            self.logger.info("Memoria limpiada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al limpiar memoria: {e}")
            return False
