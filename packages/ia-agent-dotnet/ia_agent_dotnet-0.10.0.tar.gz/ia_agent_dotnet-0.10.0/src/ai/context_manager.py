"""
Gestor de contexto avanzado
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

from utils.logging import get_logger

logger = get_logger("context-manager")


@dataclass
class CodeContext:
    """Contexto de código"""
    file_path: str
    content: str
    language: str = "csharp"
    last_modified: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)


@dataclass
class ProjectContext:
    """Contexto de proyecto"""
    project_path: str
    name: str
    framework: str
    dependencies: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    structure: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """Contexto de sesión"""
    session_id: str
    start_time: datetime = field(default_factory=datetime.now)
    current_project: Optional[ProjectContext] = None
    code_contexts: Dict[str, CodeContext] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    active_tasks: List[str] = field(default_factory=list)


class ContextManager:
    """Gestor de contexto para mantener información relevante"""
    
    def __init__(self):
        self.logger = logger
        self.sessions: Dict[str, SessionContext] = {}
        self.current_session: Optional[SessionContext] = None
        self.global_context: Dict[str, Any] = {}
    
    def create_session(self, session_id: str) -> SessionContext:
        """Crear nueva sesión"""
        try:
            session = SessionContext(session_id=session_id)
            self.sessions[session_id] = session
            self.current_session = session
            
            self.logger.info(f"Sesión creada: {session_id}")
            return session
            
        except Exception as e:
            self.logger.error(f"Error al crear sesión: {e}")
            raise
    
    def set_current_session(self, session_id: str):
        """Establecer sesión actual"""
        if session_id in self.sessions:
            self.current_session = self.sessions[session_id]
            self.logger.info(f"Sesión actual establecida: {session_id}")
        else:
            self.logger.warning(f"Sesión no encontrada: {session_id}")
    
    def add_code_context(self, file_path: str, content: str, session_id: Optional[str] = None) -> CodeContext:
        """Agregar contexto de código"""
        try:
            session = self.current_session if not session_id else self.sessions.get(session_id)
            if not session:
                raise ValueError("No hay sesión activa")
            
            # Analizar código para extraer información
            code_context = CodeContext(
                file_path=file_path,
                content=content,
                language="csharp"
            )
            
            # Extraer clases, métodos y dependencias
            code_context.classes = self._extract_classes(content)
            code_context.methods = self._extract_methods(content)
            code_context.dependencies = self._extract_dependencies(content)
            
            session.code_contexts[file_path] = code_context
            
            self.logger.info(f"Contexto de código agregado: {file_path}")
            return code_context
            
        except Exception as e:
            self.logger.error(f"Error al agregar contexto de código: {e}")
            raise
    
    def set_project_context(self, project_path: str, name: str, framework: str, session_id: Optional[str] = None):
        """Establecer contexto de proyecto"""
        try:
            session = self.current_session if not session_id else self.sessions.get(session_id)
            if not session:
                raise ValueError("No hay sesión activa")
            
            project_context = ProjectContext(
                project_path=project_path,
                name=name,
                framework=framework
            )
            
            session.current_project = project_context
            
            self.logger.info(f"Contexto de proyecto establecido: {name}")
            
        except Exception as e:
            self.logger.error(f"Error al establecer contexto de proyecto: {e}")
            raise
    
    def add_conversation_entry(self, role: str, content: str, session_id: Optional[str] = None):
        """Agregar entrada de conversación"""
        try:
            session = self.current_session if not session_id else self.sessions.get(session_id)
            if not session:
                raise ValueError("No hay sesión activa")
            
            entry = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            session.conversation_history.append(entry)
            
            # Mantener solo las últimas 100 entradas
            if len(session.conversation_history) > 100:
                session.conversation_history = session.conversation_history[-100:]
            
        except Exception as e:
            self.logger.error(f"Error al agregar entrada de conversación: {e}")
            raise
    
    def get_relevant_context(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtener contexto relevante para una consulta"""
        try:
            session = self.current_session if not session_id else self.sessions.get(session_id)
            if not session:
                return {}
            
            relevant_context = {
                "project": session.current_project,
                "recent_code": [],
                "conversation_summary": self._summarize_conversation(session.conversation_history),
                "active_tasks": session.active_tasks
            }
            
            # Buscar código relevante basado en la consulta
            query_lower = query.lower()
            for file_path, code_context in session.code_contexts.items():
                if any(keyword in code_context.content.lower() for keyword in query_lower.split()):
                    relevant_context["recent_code"].append({
                        "file_path": file_path,
                        "classes": code_context.classes,
                        "methods": code_context.methods
                    })
            
            return relevant_context
            
        except Exception as e:
            self.logger.error(f"Error al obtener contexto relevante: {e}")
            return {}
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extraer nombres de clases del código"""
        import re
        class_pattern = r'class\s+(\w+)'
        return re.findall(class_pattern, content)
    
    def _extract_methods(self, content: str) -> List[str]:
        """Extraer nombres de métodos del código"""
        import re
        method_pattern = r'(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?\w+\s+(\w+)\s*\('
        return re.findall(method_pattern, content)
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extraer dependencias del código"""
        import re
        using_pattern = r'using\s+([^;]+);'
        return re.findall(using_pattern, content)
    
    def _summarize_conversation(self, history: List[Dict[str, Any]]) -> str:
        """Resumir historial de conversación"""
        if not history:
            return "No hay historial de conversación"
        
        # Tomar las últimas 5 entradas
        recent = history[-5:]
        summary = "Conversación reciente:\n"
        
        for entry in recent:
            role = entry.get("role", "unknown")
            content = entry.get("content", "")[:100] + "..." if len(entry.get("content", "")) > 100 else entry.get("content", "")
            summary += f"- {role}: {content}\n"
        
        return summary
    
    def save_session(self, session_id: str, file_path: str):
        """Guardar sesión en archivo"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Sesión no encontrada: {session_id}")
            
            # Convertir a diccionario serializable
            session_data = {
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat(),
                "current_project": session.current_project.__dict__ if session.current_project else None,
                "code_contexts": {k: v.__dict__ for k, v in session.code_contexts.items()},
                "conversation_history": session.conversation_history,
                "active_tasks": session.active_tasks
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Sesión guardada: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error al guardar sesión: {e}")
            raise
    
    def load_session(self, file_path: str) -> str:
        """Cargar sesión desde archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            session_id = session_data["session_id"]
            
            # Reconstruir sesión
            session = SessionContext(session_id=session_id)
            session.start_time = datetime.fromisoformat(session_data["start_time"])
            
            if session_data["current_project"]:
                project_data = session_data["current_project"]
                session.current_project = ProjectContext(**project_data)
            
            for file_path, code_data in session_data["code_contexts"].items():
                code_data["last_modified"] = datetime.fromisoformat(code_data["last_modified"])
                session.code_contexts[file_path] = CodeContext(**code_data)
            
            session.conversation_history = session_data["conversation_history"]
            session.active_tasks = session_data["active_tasks"]
            
            self.sessions[session_id] = session
            self.current_session = session
            
            self.logger.info(f"Sesión cargada: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error al cargar sesión: {e}")
            raise
