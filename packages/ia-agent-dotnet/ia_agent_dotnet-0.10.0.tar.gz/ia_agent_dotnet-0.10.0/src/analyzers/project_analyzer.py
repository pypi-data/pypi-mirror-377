"""
Analizador de proyectos .NET
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import xml.etree.ElementTree as ET

from utils.logging import get_logger

logger = get_logger("project-analyzer")


class ProjectAnalyzer:
    """Analizador de proyectos .NET"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_project(self, project_path: Path) -> Dict[str, Any]:
        """Analizar proyecto .NET"""
        try:
            if not project_path.exists():
                raise FileNotFoundError(f"Proyecto no encontrado: {project_path}")
            
            analysis = {
                'project_path': str(project_path),
                'project_name': project_path.stem,
                'project_type': self._detect_project_type(project_path),
                'target_framework': self._get_target_framework(project_path),
                'packages': self._get_packages(project_path),
                'references': self._get_references(project_path),
                'files': self._get_project_files(project_path)
            }
            
            self.logger.info(f"Proyecto analizado: {project_path.name}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error al analizar proyecto {project_path}: {e}")
            raise
    
    def _detect_project_type(self, project_path: Path) -> str:
        """Detectar tipo de proyecto"""
        if project_path.suffix == '.csproj':
            return 'C# Project'
        elif project_path.suffix == '.vbproj':
            return 'VB.NET Project'
        elif project_path.suffix == '.fsproj':
            return 'F# Project'
        else:
            return 'Unknown'
    
    def _get_target_framework(self, project_path: Path) -> Optional[str]:
        """Obtener framework objetivo"""
        try:
            tree = ET.parse(project_path)
            root = tree.getroot()
            
            # Buscar TargetFramework
            target_framework = root.find('.//TargetFramework')
            if target_framework is not None:
                return target_framework.text
            
            # Buscar TargetFrameworks (múltiples)
            target_frameworks = root.find('.//TargetFrameworks')
            if target_frameworks is not None:
                return target_frameworks.text
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error al obtener target framework: {e}")
            return None
    
    def _get_packages(self, project_path: Path) -> List[Dict[str, str]]:
        """Obtener paquetes NuGet"""
        try:
            tree = ET.parse(project_path)
            root = tree.getroot()
            
            packages = []
            for package_ref in root.findall('.//PackageReference'):
                packages.append({
                    'name': package_ref.get('Include', ''),
                    'version': package_ref.get('Version', '')
                })
            
            return packages
            
        except Exception as e:
            self.logger.warning(f"Error al obtener paquetes: {e}")
            return []
    
    def _get_references(self, project_path: Path) -> List[Dict[str, str]]:
        """Obtener referencias de proyecto"""
        try:
            tree = ET.parse(project_path)
            root = tree.getroot()
            
            references = []
            for project_ref in root.findall('.//ProjectReference'):
                references.append({
                    'path': project_ref.get('Include', ''),
                    'name': Path(project_ref.get('Include', '')).stem
                })
            
            return references
            
        except Exception as e:
            self.logger.warning(f"Error al obtener referencias: {e}")
            return []
    
    def _get_project_files(self, project_path: Path) -> List[str]:
        """Obtener archivos del proyecto"""
        try:
            tree = ET.parse(project_path)
            root = tree.getroot()
            
            files = []
            for compile in root.findall('.//Compile'):
                include = compile.get('Include')
                if include:
                    files.append(include)
            
            return files
            
        except Exception as e:
            self.logger.warning(f"Error al obtener archivos: {e}")
            return []
