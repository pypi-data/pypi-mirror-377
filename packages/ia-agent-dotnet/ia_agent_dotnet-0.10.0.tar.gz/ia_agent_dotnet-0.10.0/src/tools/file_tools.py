"""
Herramientas para operaciones de archivos
IA Agent para Generación de Pruebas Unitarias .NET
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from utils.helpers import file_helper, validation_helper
from utils.logging import get_logger

logger = get_logger("file-tools")


@dataclass
class FileOperation:
    """Operación de archivo"""
    operation_type: str  # 'read', 'write', 'copy', 'move', 'delete'
    source_path: Optional[str] = None
    target_path: Optional[str] = None
    content: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None


class FileManager:
    """Gestor de archivos del agente"""
    
    def __init__(self, base_directory: Optional[str] = None):
        self.base_directory = Path(base_directory) if base_directory else Path.cwd()
        self.logger = logger
        self.operations_history: List[FileOperation] = []
    
    def read_file(self, file_path: Union[str, Path]) -> str:
        """Leer archivo"""
        try:
            full_path = self._resolve_path(file_path)
            self.logger.info(f"Leyendo archivo: {full_path}")
            
            content = file_helper.read_file(full_path)
            
            # Registrar operación
            operation = FileOperation(
                operation_type='read',
                source_path=str(full_path),
                success=True
            )
            self.operations_history.append(operation)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error al leer archivo {file_path}: {e}")
            
            operation = FileOperation(
                operation_type='read',
                source_path=str(file_path),
                success=False,
                error_message=str(e)
            )
            self.operations_history.append(operation)
            
            raise
    
    def write_file(self, file_path: Union[str, Path], content: str, 
                   backup: bool = True) -> bool:
        """Escribir archivo"""
        try:
            full_path = self._resolve_path(file_path)
            self.logger.info(f"Escribiendo archivo: {full_path}")
            
            # Crear backup si el archivo existe
            if backup and full_path.exists():
                backup_path = file_helper.backup_file(full_path)
                self.logger.info(f"Backup creado: {backup_path}")
            
            success = file_helper.write_file(full_path, content)
            
            # Registrar operación
            operation = FileOperation(
                operation_type='write',
                target_path=str(full_path),
                content=content[:100] + "..." if len(content) > 100 else content,
                success=success
            )
            self.operations_history.append(operation)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error al escribir archivo {file_path}: {e}")
            
            operation = FileOperation(
                operation_type='write',
                target_path=str(file_path),
                content=content[:100] + "..." if len(content) > 100 else content,
                success=False,
                error_message=str(e)
            )
            self.operations_history.append(operation)
            
            raise
    
    def copy_file(self, source_path: Union[str, Path], 
                  target_path: Union[str, Path]) -> bool:
        """Copiar archivo"""
        try:
            source_full = self._resolve_path(source_path)
            target_full = self._resolve_path(target_path)
            
            self.logger.info(f"Copiando archivo: {source_full} -> {target_full}")
            
            # Crear directorio destino si no existe
            target_full.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_full, target_full)
            
            # Registrar operación
            operation = FileOperation(
                operation_type='copy',
                source_path=str(source_full),
                target_path=str(target_full),
                success=True
            )
            self.operations_history.append(operation)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al copiar archivo {source_path} -> {target_path}: {e}")
            
            operation = FileOperation(
                operation_type='copy',
                source_path=str(source_path),
                target_path=str(target_path),
                success=False,
                error_message=str(e)
            )
            self.operations_history.append(operation)
            
            raise
    
    def move_file(self, source_path: Union[str, Path], 
                  target_path: Union[str, Path]) -> bool:
        """Mover archivo"""
        try:
            source_full = self._resolve_path(source_path)
            target_full = self._resolve_path(target_path)
            
            self.logger.info(f"Moviendo archivo: {source_full} -> {target_full}")
            
            # Crear directorio destino si no existe
            target_full.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_full), str(target_full))
            
            # Registrar operación
            operation = FileOperation(
                operation_type='move',
                source_path=str(source_full),
                target_path=str(target_full),
                success=True
            )
            self.operations_history.append(operation)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al mover archivo {source_path} -> {target_path}: {e}")
            
            operation = FileOperation(
                operation_type='move',
                source_path=str(source_path),
                target_path=str(target_path),
                success=False,
                error_message=str(e)
            )
            self.operations_history.append(operation)
            
            raise
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """Eliminar archivo"""
        try:
            full_path = self._resolve_path(file_path)
            self.logger.info(f"Eliminando archivo: {full_path}")
            
            if full_path.exists():
                full_path.unlink()
            
            # Registrar operación
            operation = FileOperation(
                operation_type='delete',
                source_path=str(full_path),
                success=True
            )
            self.operations_history.append(operation)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al eliminar archivo {file_path}: {e}")
            
            operation = FileOperation(
                operation_type='delete',
                source_path=str(file_path),
                success=False,
                error_message=str(e)
            )
            self.operations_history.append(operation)
            
            raise
    
    def create_directory(self, directory_path: Union[str, Path]) -> bool:
        """Crear directorio"""
        try:
            full_path = self._resolve_path(directory_path)
            self.logger.info(f"Creando directorio: {full_path}")
            
            full_path.mkdir(parents=True, exist_ok=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Error al crear directorio {directory_path}: {e}")
            raise
    
    def list_files(self, directory_path: Union[str, Path], 
                   pattern: str = "*") -> List[Path]:
        """Listar archivos en directorio"""
        try:
            full_path = self._resolve_path(directory_path)
            self.logger.info(f"Listando archivos en: {full_path} con patrón: {pattern}")
            
            if not full_path.exists() or not full_path.is_dir():
                return []
            
            return list(full_path.glob(pattern))
            
        except Exception as e:
            self.logger.error(f"Error al listar archivos en {directory_path}: {e}")
            raise
    
    def find_files(self, pattern: str, 
                   directory_path: Optional[Union[str, Path]] = None) -> List[Path]:
        """Buscar archivos con patrón"""
        try:
            search_path = self._resolve_path(directory_path) if directory_path else self.base_directory
            self.logger.info(f"Buscando archivos con patrón '{pattern}' en: {search_path}")
            
            return file_helper.find_files(pattern, search_path)
            
        except Exception as e:
            self.logger.error(f"Error al buscar archivos con patrón '{pattern}': {e}")
            raise
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Obtener información de archivo"""
        try:
            full_path = self._resolve_path(file_path)
            
            if not full_path.exists():
                return {'exists': False}
            
            stat = full_path.stat()
            
            return {
                'exists': True,
                'path': str(full_path),
                'name': full_path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'is_file': full_path.is_file(),
                'is_directory': full_path.is_dir(),
                'extension': full_path.suffix,
                'hash': file_helper.get_file_hash(full_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error al obtener información de archivo {file_path}: {e}")
            raise
    
    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """Resolver ruta relativa o absoluta"""
        path = Path(path)
        
        if path.is_absolute():
            return path
        
        return self.base_directory / path
    
    def get_operations_history(self) -> List[FileOperation]:
        """Obtener historial de operaciones"""
        return self.operations_history.copy()
    
    def clear_operations_history(self):
        """Limpiar historial de operaciones"""
        self.operations_history.clear()


class CodeFileManager(FileManager):
    """Gestor especializado para archivos de código"""
    
    def __init__(self, base_directory: Optional[str] = None):
        super().__init__(base_directory)
        self.supported_extensions = {'.cs', '.csproj', '.sln', '.json', '.yaml', '.yml'}
    
    def read_code_file(self, file_path: Union[str, Path]) -> str:
        """Leer archivo de código"""
        full_path = self._resolve_path(file_path)
        
        if full_path.suffix not in self.supported_extensions:
            raise ValueError(f"Tipo de archivo no soportado: {full_path.suffix}")
        
        return self.read_file(full_path)
    
    def write_code_file(self, file_path: Union[str, Path], content: str,
                       format_code: bool = True) -> bool:
        """Escribir archivo de código"""
        try:
            if format_code and file_path.endswith('.cs'):
                content = self._format_csharp_code(content)
            
            return self.write_file(file_path, content)
            
        except Exception as e:
            self.logger.error(f"Error al escribir archivo de código {file_path}: {e}")
            raise
    
    def _format_csharp_code(self, code: str) -> str:
        """Formatear código C# básico"""
        # Formateo básico - en una implementación real se usaría un formateador profesional
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Reducir indentación para llaves de cierre
            if stripped.startswith('}') or stripped.startswith(']') or stripped.startswith(')'):
                indent_level = max(0, indent_level - 1)
            
            # Agregar línea con indentación
            formatted_lines.append('    ' * indent_level + stripped)
            
            # Aumentar indentación para llaves de apertura
            if stripped.endswith('{') or stripped.endswith('[') or stripped.endswith('('):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def find_csharp_files(self, directory_path: Optional[Union[str, Path]] = None) -> List[Path]:
        """Buscar archivos C#"""
        return self.find_files("*.cs", directory_path)
    
    def find_project_files(self, directory_path: Optional[Union[str, Path]] = None) -> List[Path]:
        """Buscar archivos de proyecto"""
        project_files = []
        project_files.extend(self.find_files("*.csproj", directory_path))
        project_files.extend(self.find_files("*.sln", directory_path))
        return project_files


# Instancias globales
file_manager = FileManager()
code_file_manager = CodeFileManager()
