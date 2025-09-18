"""
Utilidades y funciones auxiliares
IA Agent para Generación de Pruebas Unitarias .NET
"""

import os
import json
import yaml
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import hashlib


class FileHelper:
    """Utilidades para manejo de archivos"""
    
    @staticmethod
    def read_file(file_path: Union[str, Path]) -> str:
        """Leer contenido de archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error al leer archivo {file_path}: {e}")
    
    @staticmethod
    def write_file(file_path: Union[str, Path], content: str) -> bool:
        """Escribir contenido a archivo"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise Exception(f"Error al escribir archivo {file_path}: {e}")
    
    @staticmethod
    def file_exists(file_path: Union[str, Path]) -> bool:
        """Verificar si archivo existe"""
        return Path(file_path).exists()
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path]) -> str:
        """Obtener hash MD5 de archivo"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    @staticmethod
    def find_files(pattern: str, directory: Union[str, Path]) -> List[Path]:
        """Buscar archivos con patrón"""
        directory = Path(directory)
        return list(directory.rglob(pattern))
    
    @staticmethod
    def backup_file(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> str:
        """Crear backup de archivo"""
        file_path = Path(file_path)
        
        if backup_dir is None:
            backup_dir = file_path.parent / "backups"
        else:
            backup_dir = Path(backup_dir)
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return str(backup_path)


class JsonHelper:
    """Utilidades para manejo de JSON"""
    
    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Cargar archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error al cargar JSON {file_path}: {e}")
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2) -> bool:
        """Guardar datos como JSON"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            raise Exception(f"Error al guardar JSON {file_path}: {e}")
    
    @staticmethod
    def parse_json(json_string: str) -> Dict[str, Any]:
        """Parsear string JSON"""
        try:
            return json.loads(json_string)
        except Exception as e:
            raise Exception(f"Error al parsear JSON: {e}")
    
    @staticmethod
    def dumps(data: Any, indent: int = 2) -> str:
        """Convertir objeto a string JSON"""
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Error al convertir a JSON: {e}")
    
    @staticmethod
    def loads(json_string: str) -> Any:
        """Convertir string JSON a objeto"""
        try:
            return json.loads(json_string)
        except Exception as e:
            raise Exception(f"Error al convertir desde JSON: {e}")


class YamlHelper:
    """Utilidades para manejo de YAML"""
    
    @staticmethod
    def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Cargar archivo YAML"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Error al cargar YAML {file_path}: {e}")
    
    @staticmethod
    def save_yaml(data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """Guardar datos como YAML"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            raise Exception(f"Error al guardar YAML {file_path}: {e}")


class DotNetHelper:
    """Utilidades para .NET"""
    
    @staticmethod
    def find_dotnet_sdk() -> Optional[str]:
        """Encontrar ruta del SDK de .NET"""
        try:
            result = subprocess.run(['dotnet', '--info'], 
                                  capture_output=True, text=True, check=True)
            
            # Buscar la ruta del SDK en la salida
            for line in result.stdout.split('\n'):
                if 'Base Path:' in line:
                    return line.split('Base Path:')[1].strip()
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def execute_dotnet_command(command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Ejecutar comando de .NET"""
        try:
            result = subprocess.run(
                ['dotnet'] + command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'stdout': e.stdout,
                'stderr': e.stderr,
                'return_code': e.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'return_code': -1
            }
    
    @staticmethod
    def find_csproj_files(directory: Union[str, Path]) -> List[Path]:
        """Encontrar archivos .csproj en directorio"""
        directory = Path(directory)
        return list(directory.rglob("*.csproj"))
    
    @staticmethod
    def get_project_info(csproj_path: Union[str, Path]) -> Dict[str, Any]:
        """Obtener información de proyecto .csproj"""
        try:
            csproj_path = Path(csproj_path)
            content = FileHelper.read_file(csproj_path)
            
            # Parsear información básica del proyecto
            info = {
                'path': str(csproj_path),
                'name': csproj_path.stem,
                'directory': str(csproj_path.parent),
                'target_framework': None,
                'packages': [],
                'references': []
            }
            
            # Buscar TargetFramework
            import re
            target_framework_match = re.search(r'<TargetFramework>(.*?)</TargetFramework>', content)
            if target_framework_match:
                info['target_framework'] = target_framework_match.group(1)
            
            # Buscar PackageReference
            package_matches = re.findall(r'<PackageReference Include="([^"]*)" Version="([^"]*)"', content)
            info['packages'] = [{'name': name, 'version': version} for name, version in package_matches]
            
            # Buscar ProjectReference
            project_matches = re.findall(r'<ProjectReference Include="([^"]*)"', content)
            info['references'] = [{'path': path} for path in project_matches]
            
            return info
        except Exception as e:
            raise Exception(f"Error al obtener información del proyecto {csproj_path}: {e}")


class StringHelper:
    """Utilidades para manejo de strings"""
    
    @staticmethod
    def to_pascal_case(text: str) -> str:
        """Convertir a PascalCase"""
        return ''.join(word.capitalize() for word in text.replace('_', ' ').replace('-', ' ').split())
    
    @staticmethod
    def to_camel_case(text: str) -> str:
        """Convertir a camelCase"""
        pascal = StringHelper.to_pascal_case(text)
        return pascal[0].lower() + pascal[1:] if pascal else ""
    
    @staticmethod
    def to_snake_case(text: str) -> str:
        """Convertir a snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def clean_string(text: str) -> str:
        """Limpiar string de caracteres especiales"""
        import re
        return re.sub(r'[^\w\s-]', '', text).strip()
    
    @staticmethod
    def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncar string a longitud máxima"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix


class ValidationHelper:
    """Utilidades para validación"""
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> bool:
        """Validar que ruta de archivo sea válida"""
        try:
            path = Path(file_path)
            return path.exists() and path.is_file()
        except Exception:
            return False
    
    @staticmethod
    def validate_directory_path(directory_path: Union[str, Path]) -> bool:
        """Validar que ruta de directorio sea válida"""
        try:
            path = Path(directory_path)
            return path.exists() and path.is_dir()
        except Exception:
            return False
    
    @staticmethod
    def validate_cs_file(file_path: Union[str, Path]) -> bool:
        """Validar que archivo sea .cs válido"""
        try:
            path = Path(file_path)
            return (path.exists() and 
                   path.is_file() and 
                   path.suffix.lower() == '.cs')
        except Exception:
            return False
    
    @staticmethod
    def validate_csproj_file(file_path: Union[str, Path]) -> bool:
        """Validar que archivo sea .csproj válido"""
        try:
            path = Path(file_path)
            return (path.exists() and 
                   path.is_file() and 
                   path.suffix.lower() == '.csproj')
        except Exception:
            return False


class TimeHelper:
    """Utilidades para manejo de tiempo"""
    
    @staticmethod
    def get_timestamp() -> str:
        """Obtener timestamp actual"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_timestamp_filename() -> str:
        """Obtener timestamp para nombres de archivo"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Formatear duración en segundos"""
        if seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.2f}h"


# Instancias globales de helpers
file_helper = FileHelper()
json_helper = JsonHelper()
yaml_helper = YamlHelper()
dotnet_helper = DotNetHelper()
string_helper = StringHelper()
validation_helper = ValidationHelper()
time_helper = TimeHelper()
