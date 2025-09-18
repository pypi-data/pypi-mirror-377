"""
Analizador de dependencias .NET
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import json

from utils.logging import get_logger

logger = get_logger("dependency-analyzer")


class DependencyAnalyzer:
    """Analizador de dependencias .NET"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Analizar dependencias del proyecto"""
        try:
            analysis = {
                'project_path': str(project_path),
                'direct_dependencies': self._get_direct_dependencies(project_path),
                'transitive_dependencies': self._get_transitive_dependencies(project_path),
                'dependency_tree': self._build_dependency_tree(project_path),
                'conflicts': self._detect_conflicts(project_path),
                'outdated_packages': self._check_outdated_packages(project_path)
            }
            
            self.logger.info(f"Dependencias analizadas: {project_path.name}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error al analizar dependencias {project_path}: {e}")
            raise
    
    def _get_direct_dependencies(self, project_path: Path) -> List[Dict[str, str]]:
        """Obtener dependencias directas"""
        try:
            # Buscar archivos de proyecto
            project_files = list(project_path.parent.glob("*.csproj"))
            if not project_files:
                return []
            
            dependencies = []
            for proj_file in project_files:
                # Leer archivo de proyecto y extraer PackageReference
                content = proj_file.read_text(encoding='utf-8')
                
                # Parsear PackageReference (simplificado)
                import re
                package_pattern = r'<PackageReference Include="([^"]*)" Version="([^"]*)"'
                
                for match in re.finditer(package_pattern, content):
                    dependencies.append({
                        'name': match.group(1),
                        'version': match.group(2),
                        'type': 'package'
                    })
            
            return dependencies
            
        except Exception as e:
            self.logger.warning(f"Error al obtener dependencias directas: {e}")
            return []
    
    def _get_transitive_dependencies(self, project_path: Path) -> List[Dict[str, str]]:
        """Obtener dependencias transitivas"""
        # En una implementación real, esto requeriría ejecutar 'dotnet list package --include-transitive'
        # Por ahora, retornamos una lista vacía
        return []
    
    def _build_dependency_tree(self, project_path: Path) -> Dict[str, Any]:
        """Construir árbol de dependencias"""
        try:
            tree = {
                'root': project_path.name,
                'dependencies': self._get_direct_dependencies(project_path),
                'children': []
            }
            
            return tree
            
        except Exception as e:
            self.logger.warning(f"Error al construir árbol de dependencias: {e}")
            return {}
    
    def _detect_conflicts(self, project_path: Path) -> List[Dict[str, Any]]:
        """Detectar conflictos de dependencias"""
        # En una implementación real, esto detectaría versiones conflictivas
        return []
    
    def _check_outdated_packages(self, project_path: Path) -> List[Dict[str, str]]:
        """Verificar paquetes desactualizados"""
        # En una implementación real, esto verificaría versiones más recientes
        return []
