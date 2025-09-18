"""
Herramientas de análisis en memoria para código C#
IA Agent para Generación de Pruebas Unitarias .NET
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from utils.logging import get_logger

logger = get_logger("memory-analysis-tools")


@dataclass
class ControllerInfo:
    """Información de un controlador extraída de código en memoria"""
    name: str
    namespace: str
    base_class: str
    route: str
    methods: List[Dict[str, Any]]
    dependencies: List[str]


@dataclass
class ModelInfo:
    """Información de un modelo extraído de código en memoria"""
    name: str
    namespace: str
    properties: List[Dict[str, str]]
    type: str  # 'entity', 'dto', 'request', 'response'


@dataclass
class ServiceInfo:
    """Información de un servicio extraído de código en memoria"""
    name: str
    interface_name: Optional[str]
    namespace: str
    methods: List[Dict[str, Any]]
    dependencies: List[str]


class MemoryCodeAnalyzer:
    """Analizador de código C# en memoria"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_code_content(self, code_content: str) -> Dict[str, Any]:
        """Analizar contenido de código C# completo"""
        try:
            self.logger.info("Iniciando análisis de código en memoria")
            
            # Dividir el código en archivos lógicos
            files = self._split_code_into_files(code_content)
            
            # Analizar cada archivo
            controllers = []
            models = []
            services = []
            dependencies = []
            
            for file_name, file_content in files.items():
                self.logger.info(f"Analizando archivo: {file_name}")
                
                # Analizar controladores
                if self._is_controller_file(file_name, file_content):
                    controller = self._analyze_controller_content(file_name, file_content)
                    if controller:
                        controllers.append(controller)
                
                # Analizar modelos
                elif self._is_model_file(file_name, file_content):
                    model = self._analyze_model_content(file_name, file_content)
                    if model:
                        models.append(model)
                
                # Analizar servicios
                elif self._is_service_file(file_name, file_content):
                    service = self._analyze_service_content(file_name, file_content)
                    if service:
                        services.append(service)
                
                # Extraer dependencias de Program.cs
                elif "Program.cs" in file_name:
                    dependencies = self._extract_dependencies_from_program(file_content)
            
            return {
                "success": True,
                "controllers": [self._controller_to_dict(c) for c in controllers],
                "models": [self._model_to_dict(m) for m in models],
                "services": [self._service_to_dict(s) for s in services],
                "dependencies": dependencies,
                "summary": {
                    "total_controllers": len(controllers),
                    "total_models": len(models),
                    "total_services": len(services),
                    "total_dependencies": len(dependencies)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error al analizar código en memoria: {e}")
            return {
                "success": False,
                "error": str(e),
                "controllers": [],
                "models": [],
                "services": [],
                "dependencies": []
            }
    
    def _split_code_into_files(self, code_content: str) -> Dict[str, str]:
        """Dividir el código en archivos lógicos basado en comentarios"""
        files = {}
        current_file = None
        current_content = []
        
        lines = code_content.split('\n')
        
        for line in lines:
            # Detectar inicio de archivo
            if line.strip().startswith('// ') and ('.cs' in line or 'Program.cs' in line):
                # Guardar archivo anterior
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)
                
                # Iniciar nuevo archivo
                current_file = line.strip()[3:]  # Remover '// '
                current_content = [line]
            else:
                if current_file:
                    current_content.append(line)
        
        # Guardar último archivo
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)
        
        return files
    
    def _is_controller_file(self, file_name: str, content: str) -> bool:
        """Verificar si es un archivo de controlador"""
        return ("Controller" in file_name or 
                "Controller" in content and "ApiController" in content)
    
    def _is_model_file(self, file_name: str, content: str) -> bool:
        """Verificar si es un archivo de modelo"""
        return ("Model" in file_name or 
                "class " in content and not "Controller" in content and not "Service" in content)
    
    def _is_service_file(self, file_name: str, content: str) -> bool:
        """Verificar si es un archivo de servicio"""
        return ("Service" in file_name or 
                "Service" in content and ("interface" in content or "class" in content))
    
    def _analyze_controller_content(self, file_name: str, content: str) -> Optional[ControllerInfo]:
        """Analizar contenido de controlador"""
        try:
            # Extraer nombre de la clase
            class_match = re.search(r'public\s+class\s+(\w+)', content)
            if not class_match:
                return None
            
            class_name = class_match.group(1)
            
            # Extraer namespace
            namespace_match = re.search(r'namespace\s+([\w.]+)', content)
            namespace = namespace_match.group(1) if namespace_match else "Unknown"
            
            # Extraer clase base
            base_match = re.search(r'public\s+class\s+\w+\s*:\s*(\w+)', content)
            base_class = base_match.group(1) if base_match else "ControllerBase"
            
            # Extraer ruta base
            route_match = re.search(r'\[Route\("([^"]*)"\)\]', content)
            route = route_match.group(1) if route_match else "api/[controller]"
            
            # Extraer métodos
            methods = self._extract_controller_methods(content)
            
            # Extraer dependencias del constructor
            dependencies = self._extract_constructor_dependencies(content)
            
            return ControllerInfo(
                name=class_name,
                namespace=namespace,
                base_class=base_class,
                route=route,
                methods=methods,
                dependencies=dependencies
            )
            
        except Exception as e:
            self.logger.error(f"Error al analizar controlador {file_name}: {e}")
            return None
    
    def _extract_controller_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extraer métodos de controlador"""
        methods = []
        
        # Patrón para métodos de controlador
        method_pattern = r'(\[.*?\])?\s*public\s+(\w+)\s+(\w+)\s*\(([^)]*)\)'
        
        for match in re.finditer(method_pattern, content, re.MULTILINE | re.DOTALL):
            attributes_text = match.group(1) or ""
            return_type = match.group(2)
            method_name = match.group(3)
            parameters_text = match.group(4)
            
            # Extraer método HTTP
            http_method = self._extract_http_method(attributes_text)
            
            # Extraer ruta específica
            route = self._extract_method_route(attributes_text)
            
            # Extraer parámetros
            parameters = self._extract_method_parameters(parameters_text)
            
            methods.append({
                "name": method_name,
                "return_type": return_type,
                "http_method": http_method,
                "route": route,
                "parameters": parameters,
                "attributes": self._extract_attributes(attributes_text)
            })
        
        return methods
    
    def _extract_http_method(self, attributes_text: str) -> Optional[str]:
        """Extraer método HTTP de atributos"""
        http_methods = ['HttpGet', 'HttpPost', 'HttpPut', 'HttpDelete', 'HttpPatch']
        
        for method in http_methods:
            if method in attributes_text:
                return method.replace('Http', '').upper()
        
        return None
    
    def _extract_method_route(self, attributes_text: str) -> Optional[str]:
        """Extraer ruta específica del método"""
        route_match = re.search(r'\[Http\w+\("([^"]*)"\)\]', attributes_text)
        return route_match.group(1) if route_match else None
    
    def _extract_method_parameters(self, parameters_text: str) -> List[Dict[str, str]]:
        """Extraer parámetros del método"""
        parameters = []
        
        if not parameters_text.strip():
            return parameters
        
        param_parts = [p.strip() for p in parameters_text.split(',')]
        
        for param in param_parts:
            param_match = re.search(r'(\[.*?\])?\s*(\w+)\s+(\w+)', param)
            if param_match:
                attributes = param_match.group(1) or ""
                param_type = param_match.group(2)
                param_name = param_match.group(3)
                
                parameters.append({
                    "name": param_name,
                    "type": param_type,
                    "attributes": attributes
                })
        
        return parameters
    
    def _extract_attributes(self, attributes_text: str) -> List[str]:
        """Extraer atributos"""
        attributes = []
        attr_matches = re.findall(r'\[([^\]]+)\]', attributes_text)
        attributes.extend(attr_matches)
        return attributes
    
    def _extract_constructor_dependencies(self, content: str) -> List[str]:
        """Extraer dependencias del constructor"""
        dependencies = []
        
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
    
    def _analyze_model_content(self, file_name: str, content: str) -> Optional[ModelInfo]:
        """Analizar contenido de modelo"""
        try:
            # Extraer nombre de la clase
            class_match = re.search(r'public\s+class\s+(\w+)', content)
            if not class_match:
                return None
            
            class_name = class_match.group(1)
            
            # Extraer namespace
            namespace_match = re.search(r'namespace\s+([\w.]+)', content)
            namespace = namespace_match.group(1) if namespace_match else "Unknown"
            
            # Extraer propiedades
            properties = self._extract_properties(content)
            
            # Determinar tipo de modelo
            model_type = self._determine_model_type(class_name, content)
            
            return ModelInfo(
                name=class_name,
                namespace=namespace,
                properties=properties,
                type=model_type
            )
            
        except Exception as e:
            self.logger.error(f"Error al analizar modelo {file_name}: {e}")
            return None
    
    def _extract_properties(self, content: str) -> List[Dict[str, str]]:
        """Extraer propiedades de una clase"""
        properties = []
        
        # Patrón para propiedades
        prop_pattern = r'public\s+(\w+)\s+(\w+)\s*\{\s*get;\s*set;\s*\}'
        
        for match in re.finditer(prop_pattern, content):
            prop_type = match.group(1)
            prop_name = match.group(2)
            
            properties.append({
                "name": prop_name,
                "type": prop_type
            })
        
        return properties
    
    def _determine_model_type(self, class_name: str, content: str) -> str:
        """Determinar tipo de modelo"""
        if "Request" in class_name:
            return "request"
        elif "Response" in class_name or "Result" in class_name:
            return "response"
        elif "Dto" in class_name:
            return "dto"
        else:
            return "entity"
    
    def _analyze_service_content(self, file_name: str, content: str) -> Optional[ServiceInfo]:
        """Analizar contenido de servicio"""
        try:
            # Verificar si es interfaz o implementación
            is_interface = "interface" in content
            
            if is_interface:
                # Analizar interfaz
                interface_match = re.search(r'public\s+interface\s+(\w+)', content)
                if not interface_match:
                    return None
                
                interface_name = interface_match.group(1)
                class_name = interface_name
            else:
                # Analizar implementación
                class_match = re.search(r'public\s+class\s+(\w+)', content)
                if not class_match:
                    return None
                
                class_name = class_match.group(1)
                
                # Buscar interfaz implementada
                interface_match = re.search(r'public\s+class\s+\w+\s*:\s*(\w+)', content)
                interface_name = interface_match.group(1) if interface_match else None
            
            # Extraer namespace
            namespace_match = re.search(r'namespace\s+([\w.]+)', content)
            namespace = namespace_match.group(1) if namespace_match else "Unknown"
            
            # Extraer métodos
            methods = self._extract_service_methods(content)
            
            # Extraer dependencias del constructor
            dependencies = self._extract_constructor_dependencies(content)
            
            return ServiceInfo(
                name=class_name,
                interface_name=interface_name,
                namespace=namespace,
                methods=methods,
                dependencies=dependencies
            )
            
        except Exception as e:
            self.logger.error(f"Error al analizar servicio {file_name}: {e}")
            return None
    
    def _extract_service_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extraer métodos de servicio"""
        methods = []
        
        # Patrón para métodos de servicio
        method_pattern = r'public\s+(\w+)\s+(\w+)\s*\(([^)]*)\)'
        
        for match in re.finditer(method_pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)
            parameters_text = match.group(3)
            
            # Extraer parámetros
            parameters = self._extract_method_parameters(parameters_text)
            
            methods.append({
                "name": method_name,
                "return_type": return_type,
                "parameters": parameters
            })
        
        return methods
    
    def _extract_dependencies_from_program(self, content: str) -> List[Dict[str, str]]:
        """Extraer dependencias registradas en Program.cs"""
        dependencies = []
        
        # Buscar registros de servicios
        service_pattern = r'builder\.Services\.Add\w+<([^,>]+),\s*([^>]+)>\(\)'
        
        for match in re.finditer(service_pattern, content):
            interface_name = match.group(1)
            implementation_name = match.group(2)
            
            dependencies.append({
                "interface": interface_name,
                "implementation": implementation_name,
                "lifetime": "scoped"  # Por defecto
            })
        
        return dependencies
    
    def _controller_to_dict(self, controller: ControllerInfo) -> Dict[str, Any]:
        """Convertir ControllerInfo a diccionario"""
        return {
            "name": controller.name,
            "namespace": controller.namespace,
            "base_class": controller.base_class,
            "route": controller.route,
            "methods": controller.methods,
            "dependencies": controller.dependencies
        }
    
    def _model_to_dict(self, model: ModelInfo) -> Dict[str, Any]:
        """Convertir ModelInfo a diccionario"""
        return {
            "name": model.name,
            "namespace": model.namespace,
            "properties": model.properties,
            "type": model.type
        }
    
    def _service_to_dict(self, service: ServiceInfo) -> Dict[str, Any]:
        """Convertir ServiceInfo a diccionario"""
        return {
            "name": service.name,
            "interface_name": service.interface_name,
            "namespace": service.namespace,
            "methods": service.methods,
            "dependencies": service.dependencies
        }


# Instancia global
memory_analyzer = MemoryCodeAnalyzer()

