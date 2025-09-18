"""
Herramientas para análisis y manipulación de proyectos .NET
IA Agent para Generación de Pruebas Unitarias .NET
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from utils.helpers import dotnet_helper, file_helper, validation_helper
from utils.logging import get_logger

logger = get_logger("dotnet-tools")


class ProjectType(Enum):
    """Tipos de proyecto .NET"""
    WEB_API = "web-api"
    CONSOLE = "console"
    CLASS_LIBRARY = "class-library"
    TEST = "test"
    UNKNOWN = "unknown"


@dataclass
class ProjectInfo:
    """Información de un proyecto .NET"""
    name: str
    path: str
    target_framework: str
    project_type: ProjectType
    packages: List[Dict[str, str]]
    references: List[Dict[str, str]]
    source_files: List[str]
    test_framework: Optional[str] = None


@dataclass
class ControllerInfo:
    """Información de un controlador API"""
    name: str
    file_path: str
    namespace: str
    base_class: str
    methods: List[Dict[str, Any]]
    attributes: List[str]
    dependencies: List[str]


@dataclass
class MethodInfo:
    """Información de un método"""
    name: str
    return_type: str
    parameters: List[Dict[str, str]]
    attributes: List[str]
    http_method: Optional[str] = None
    route: Optional[str] = None


class DotNetProjectDiscovery:
    """Descubridor de proyectos .NET"""
    
    def __init__(self):
        self.logger = logger
    
    def discover_projects(self, root_path: str, exclude_test_projects: bool = True) -> List[ProjectInfo]:
        """Descubrir todos los proyectos .NET en un directorio"""
        projects = []
        root = Path(root_path)
        
        if not root.exists():
            self.logger.error(f"Directorio no existe: {root_path}")
            return projects
        
        self.logger.info(f"Descubriendo proyectos .NET en: {root_path}")
        
        # Buscar archivos .csproj
        for csproj_file in root.rglob("*.csproj"):
            try:
                project_info = self._analyze_project_file(csproj_file)
                if project_info:
                    # Filtrar proyectos de pruebas si se solicita
                    if exclude_test_projects and project_info.project_type == ProjectType.TEST:
                        self.logger.info(f"Excluyendo proyecto de pruebas: {project_info.name}")
                        continue
                    projects.append(project_info)
            except Exception as e:
                self.logger.warning(f"Error al analizar proyecto {csproj_file}: {e}")
        
        # Buscar archivos .sln y extraer proyectos
        for sln_file in root.rglob("*.sln"):
            try:
                solution_projects = self._analyze_solution_file(sln_file)
                # Agregar solo proyectos que no estén ya en la lista
                for proj in solution_projects:
                    if not any(p.path == proj.path for p in projects):
                        # Filtrar proyectos de pruebas si se solicita
                        if exclude_test_projects and proj.project_type == ProjectType.TEST:
                            self.logger.info(f"Excluyendo proyecto de pruebas: {proj.name}")
                            continue
                        projects.append(proj)
            except Exception as e:
                self.logger.warning(f"Error al analizar solución {sln_file}: {e}")
        
        self.logger.info(f"Encontrados {len(projects)} proyectos .NET")
        return projects
    
    def _analyze_project_file(self, csproj_path: Path) -> Optional[ProjectInfo]:
        """Analizar un archivo .csproj individual"""
        try:
            # Leer contenido del archivo
            content = csproj_path.read_text(encoding='utf-8')
            
            # Extraer información básica
            name = csproj_path.stem
            target_framework = self._extract_target_framework(content)
            project_type = self._determine_project_type(content)
            
            # Buscar archivos fuente
            source_files = self._find_source_files(csproj_path.parent)
            
            # Determinar framework de pruebas
            test_framework = self._detect_test_framework(content)
            
            return ProjectInfo(
                name=name,
                path=str(csproj_path.parent),
                target_framework=target_framework,
                project_type=project_type,
                packages=self._extract_packages(content),
                references=self._extract_references(content),
                source_files=source_files,
                test_framework=test_framework
            )
            
        except Exception as e:
            self.logger.error(f"Error al analizar {csproj_path}: {e}")
            return None
    
    def _analyze_solution_file(self, sln_path: Path) -> List[ProjectInfo]:
        """Analizar un archivo .sln y extraer proyectos"""
        projects = []
        try:
            content = sln_path.read_text(encoding='utf-8')
            
            # Buscar referencias a proyectos en el archivo .sln
            project_pattern = r'Project\("([^"]+)"\)\s*=\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"'
            matches = re.findall(project_pattern, content)
            
            for match in matches:
                project_path = Path(sln_path.parent) / match[2]
                if project_path.exists() and project_path.suffix == '.csproj':
                    project_info = self._analyze_project_file(project_path)
                    if project_info:
                        projects.append(project_info)
                        
        except Exception as e:
            self.logger.error(f"Error al analizar solución {sln_path}: {e}")
        
        return projects
    
    def _extract_target_framework(self, content: str) -> str:
        """Extraer el framework objetivo del proyecto"""
        patterns = [
            r'<TargetFramework>([^<]+)</TargetFramework>',
            r'<TargetFrameworks>([^<]+)</TargetFrameworks>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).split(';')[0]  # Tomar el primero si hay múltiples
        
        return "Unknown"
    
    def _determine_project_type(self, content: str) -> ProjectType:
        """Determinar el tipo de proyecto basado en el contenido"""
        if 'Microsoft.AspNetCore.App' in content or 'Microsoft.AspNetCore.All' in content:
            return ProjectType.WEB_API
        elif 'Microsoft.NET.Test.Sdk' in content or 'xunit' in content or 'nunit' in content or 'mstest' in content:
            return ProjectType.TEST
        elif 'Microsoft.NET.Sdk' in content and 'Exe' in content:
            return ProjectType.CONSOLE
        elif 'Microsoft.NET.Sdk' in content:
            return ProjectType.CLASS_LIBRARY
        else:
            return ProjectType.UNKNOWN
    
    def _find_source_files(self, project_dir: Path) -> List[str]:
        """Encontrar archivos fuente en el directorio del proyecto"""
        source_files = []
        for pattern in ['*.cs', '*.csproj']:
            for file_path in project_dir.rglob(pattern):
                if file_path.is_file():
                    source_files.append(str(file_path.relative_to(project_dir)))
        return source_files
    
    def _detect_test_framework(self, content: str) -> Optional[str]:
        """Detectar el framework de pruebas utilizado"""
        if 'xunit' in content.lower():
            return 'xUnit'
        elif 'nunit' in content.lower():
            return 'NUnit'
        elif 'mstest' in content.lower() or 'Microsoft.NET.Test.Sdk' in content:
            return 'MSTest'
        return None
    
    def _extract_packages(self, content: str) -> List[Dict[str, str]]:
        """Extraer paquetes NuGet del proyecto"""
        packages = []
        pattern = r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"'
        matches = re.findall(pattern, content)
        
        for match in matches:
            packages.append({
                'name': match[0],
                'version': match[1]
            })
        
        return packages
    
    def _extract_references(self, content: str) -> List[Dict[str, str]]:
        """Extraer referencias de proyecto"""
        references = []
        pattern = r'<ProjectReference\s+Include="([^"]+)"'
        matches = re.findall(pattern, content)
        
        for match in matches:
            references.append({
                'path': match,
                'name': Path(match).stem
            })
        
        return references


class DotNetProjectAnalyzer:
    """Analizador de proyectos .NET"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_project(self, project_path: str) -> ProjectInfo:
        """Analizar un proyecto .NET completo"""
        try:
            self.logger.info(f"Analizando proyecto: {project_path}")
            
            project_path = Path(project_path)
            if not project_path.exists():
                raise ValueError(f"El proyecto no existe: {project_path}")
            
            # Obtener información básica del proyecto
            csproj_files = dotnet_helper.find_csproj_files(project_path)
            if not csproj_files:
                raise ValueError(f"No se encontraron archivos .csproj en: {project_path}")
            
            main_csproj = csproj_files[0]  # Usar el primer .csproj encontrado
            project_info = dotnet_helper.get_project_info(main_csproj)
            
            # Determinar tipo de proyecto
            project_type = self._determine_project_type(project_info)
            
            # Encontrar archivos fuente
            source_files = self._find_source_files(project_path)
            
            # Detectar framework de testing
            test_framework = self._detect_test_framework(project_info)
            
            return ProjectInfo(
                name=project_info['name'],
                path=str(project_path),
                target_framework=project_info.get('target_framework', 'Unknown'),
                project_type=project_type,
                packages=project_info['packages'],
                references=project_info['references'],
                source_files=source_files,
                test_framework=test_framework
            )
            
        except Exception as e:
            self.logger.error(f"Error al analizar proyecto {project_path}: {e}")
            raise
    
    def _determine_project_type(self, project_info: Dict[str, Any]) -> ProjectType:
        """Determinar tipo de proyecto basado en paquetes y configuración"""
        packages = [pkg['name'].lower() for pkg in project_info['packages']]
        
        # Verificar si es Web API
        if any(pkg in packages for pkg in ['microsoft.aspnetcore.mvc', 'microsoft.aspnetcore.webapi']):
            return ProjectType.WEB_API
        
        # Verificar si es proyecto de testing
        if any(pkg in packages for pkg in ['microsoft.net.test.sdk', 'xunit', 'nunit', 'mstest']):
            return ProjectType.TEST
        
        # Verificar si es biblioteca de clases
        if 'microsoft.net.sdk' in str(project_info.get('target_framework', '')).lower():
            return ProjectType.CLASS_LIBRARY
        
        return ProjectType.UNKNOWN
    
    def _find_source_files(self, project_path: Path) -> List[str]:
        """Encontrar archivos fuente .cs"""
        source_files = []
        
        # Buscar archivos .cs
        for cs_file in project_path.rglob("*.cs"):
            if not any(part.startswith('.') for part in cs_file.parts):  # Ignorar archivos ocultos
                source_files.append(str(cs_file))
        
        return source_files
    
    def _detect_test_framework(self, project_info: Dict[str, Any]) -> Optional[str]:
        """Detectar framework de testing usado"""
        packages = [pkg['name'].lower() for pkg in project_info['packages']]
        
        if 'xunit' in packages:
            return 'xunit'
        elif 'nunit' in packages:
            return 'nunit'
        elif 'mstest' in packages:
            return 'mstest'
        
        return None


class DotNetControllerAnalyzer:
    """Analizador de controladores .NET"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_controller(self, controller_file: str) -> ControllerInfo:
        """Analizar un controlador API"""
        try:
            self.logger.info(f"Analizando controlador: {controller_file}")
            
            if not validation_helper.validate_cs_file(controller_file):
                raise ValueError(f"Archivo no válido: {controller_file}")
            
            content = file_helper.read_file(controller_file)
            
            # Extraer información del controlador
            name = self._extract_class_name(content)
            namespace = self._extract_namespace(content)
            base_class = self._extract_base_class(content)
            methods = self._extract_methods(content)
            attributes = self._extract_class_attributes(content)
            dependencies = self._extract_dependencies(content)
            
            return ControllerInfo(
                name=name,
                file_path=controller_file,
                namespace=namespace,
                base_class=base_class,
                methods=methods,
                attributes=attributes,
                dependencies=dependencies
            )
            
        except Exception as e:
            self.logger.error(f"Error al analizar controlador {controller_file}: {e}")
            raise
    
    def _extract_class_name(self, content: str) -> str:
        """Extraer nombre de la clase"""
        match = re.search(r'public\s+class\s+(\w+)', content)
        return match.group(1) if match else "Unknown"
    
    def _extract_namespace(self, content: str) -> str:
        """Extraer namespace"""
        match = re.search(r'namespace\s+([\w.]+)', content)
        return match.group(1) if match else "Unknown"
    
    def _extract_base_class(self, content: str) -> str:
        """Extraer clase base"""
        match = re.search(r'public\s+class\s+\w+\s*:\s*(\w+)', content)
        return match.group(1) if match else "Object"
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extraer métodos del controlador"""
        methods = []
        
        # Patrón para métodos de controlador
        method_pattern = r'(\[.*?\])?\s*public\s+(\w+)\s+(\w+)\s*\(([^)]*)\)'
        
        for match in re.finditer(method_pattern, content, re.MULTILINE | re.DOTALL):
            attributes_text = match.group(1) or ""
            return_type = match.group(2)
            method_name = match.group(3)
            parameters_text = match.group(4)
            
            # Extraer atributos HTTP
            http_method = self._extract_http_method(attributes_text)
            route = self._extract_route(attributes_text)
            
            # Extraer parámetros
            parameters = self._extract_parameters(parameters_text)
            
            # Extraer atributos
            attributes = self._extract_method_attributes(attributes_text)
            
            methods.append({
                'name': method_name,
                'return_type': return_type,
                'parameters': parameters,
                'attributes': attributes,
                'http_method': http_method,
                'route': route
            })
        
        return methods
    
    def _extract_http_method(self, attributes_text: str) -> Optional[str]:
        """Extraer método HTTP de atributos"""
        http_methods = ['HttpGet', 'HttpPost', 'HttpPut', 'HttpDelete', 'HttpPatch']
        
        for method in http_methods:
            if method in attributes_text:
                return method.replace('Http', '').upper()
        
        return None
    
    def _extract_route(self, attributes_text: str) -> Optional[str]:
        """Extraer ruta de atributos"""
        # Buscar Route attribute
        route_match = re.search(r'\[Route\("([^"]*)"\)\]', attributes_text)
        if route_match:
            return route_match.group(1)
        
        # Buscar en HttpGet, HttpPost, etc.
        route_match = re.search(r'\[Http\w+\("([^"]*)"\)\]', attributes_text)
        if route_match:
            return route_match.group(1)
        
        return None
    
    def _extract_parameters(self, parameters_text: str) -> List[Dict[str, str]]:
        """Extraer parámetros del método"""
        parameters = []
        
        if not parameters_text.strip():
            return parameters
        
        # Dividir por comas y procesar cada parámetro
        param_parts = [p.strip() for p in parameters_text.split(',')]
        
        for param in param_parts:
            # Patrón: [FromBody] Type name
            param_match = re.search(r'(\[.*?\])?\s*(\w+)\s+(\w+)', param)
            if param_match:
                attributes = param_match.group(1) or ""
                param_type = param_match.group(2)
                param_name = param_match.group(3)
                
                parameters.append({
                    'name': param_name,
                    'type': param_type,
                    'attributes': attributes
                })
        
        return parameters
    
    def _extract_class_attributes(self, content: str) -> List[str]:
        """Extraer atributos de la clase"""
        attributes = []
        
        # Buscar atributos antes de la declaración de clase
        class_match = re.search(r'(\[.*?\])*\s*public\s+class', content, re.MULTILINE | re.DOTALL)
        if class_match:
            attributes_text = class_match.group(1) or ""
            attr_matches = re.findall(r'\[([^\]]+)\]', attributes_text)
            attributes.extend(attr_matches)
        
        return attributes
    
    def _extract_method_attributes(self, attributes_text: str) -> List[str]:
        """Extraer atributos del método"""
        attributes = []
        attr_matches = re.findall(r'\[([^\]]+)\]', attributes_text)
        attributes.extend(attr_matches)
        return attributes
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extraer dependencias inyectadas"""
        dependencies = []
        
        # Buscar inyección de dependencias en constructor
        constructor_match = re.search(r'public\s+\w+\s*\(([^)]*)\)', content)
        if constructor_match:
            params_text = constructor_match.group(1)
            param_parts = [p.strip() for p in params_text.split(',')]
            
            for param in param_parts:
                param_match = re.search(r'(\w+)\s+(\w+)', param)
                if param_match:
                    param_type = param_match.group(1)
                    dependencies.append(param_type)
        
        return dependencies


class DotNetCommandExecutor:
    """Ejecutor de comandos .NET"""
    
    def __init__(self):
        self.logger = logger
    
    def execute_command(self, command: List[str], working_directory: Optional[str] = None) -> Dict[str, Any]:
        """Ejecutar comando de .NET"""
        try:
            self.logger.info(f"Ejecutando comando: dotnet {' '.join(command)}")
            
            result = dotnet_helper.execute_dotnet_command(command, working_directory)
            
            if result['success']:
                self.logger.info("Comando ejecutado exitosamente")
            else:
                self.logger.warning(f"Comando falló: {result['stderr']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error al ejecutar comando: {e}")
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'return_code': -1
            }
    
    def get_dotnet_version(self) -> str:
        """Obtener versión de .NET"""
        try:
            result = self.execute_command(['--version'])
            if result['success']:
                return result['stdout'].strip()
            else:
                return "Versión no disponible"
        except Exception as e:
            self.logger.error(f"Error al obtener versión de .NET: {e}")
            return "Error al obtener versión"
    
    def build_project(self, project_path: str) -> Dict[str, Any]:
        """Compilar proyecto"""
        return self.execute_command(['build'], project_path)
    
    def run_tests(self, project_path: str, test_filter: Optional[str] = None) -> Dict[str, Any]:
        """Ejecutar pruebas"""
        command = ['test']
        if test_filter:
            command.extend(['--filter', test_filter])
        
        return self.execute_command(command, project_path)
    
    def get_coverage(self, project_path: str) -> Dict[str, Any]:
        """Obtener cobertura de código"""
        command = ['test', '--collect:"XPlat Code Coverage"']
        return self.execute_command(command, project_path)
    
    def restore_packages(self, project_path: str) -> Dict[str, Any]:
        """Restaurar paquetes NuGet"""
        return self.execute_command(['restore'], project_path)


# Instancias globales de herramientas
project_analyzer = DotNetProjectAnalyzer()
controller_analyzer = DotNetControllerAnalyzer()
command_executor = DotNetCommandExecutor()

# Manager principal de .NET
class DotNetManager:
    """Manager principal para operaciones .NET"""
    
    def __init__(self):
        self.project_analyzer = project_analyzer
        self.controller_analyzer = controller_analyzer
        self.command_executor = command_executor
    
    def get_dotnet_version(self) -> str:
        """Obtener versión de .NET"""
        return self.command_executor.get_dotnet_version()
    
    def get_project_info(self, project_path: str) -> Dict[str, Any]:
        """Obtener información del proyecto"""
        return self.project_analyzer.analyze_project(project_path)
    
    def build_project(self, project_path: str) -> Dict[str, Any]:
        """Compilar proyecto"""
        return self.command_executor.build_project(project_path)
    
    def run_tests(self, project_path: str) -> Dict[str, Any]:
        """Ejecutar pruebas"""
        return self.command_executor.run_tests(project_path)

# Instancias globales
dotnet_manager = DotNetManager()
project_discovery = DotNetProjectDiscovery()
