"""
Analizador de código .NET
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import re
import ast

from utils.logging import get_logger

logger = get_logger("code-analyzer")


class CodeAnalyzer:
    """Analizador de código .NET"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_csharp_file(self, file_path: Path) -> Dict[str, Any]:
        """Analizar archivo C#"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            analysis = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'classes': self._extract_classes(content),
                'methods': self._extract_methods(content),
                'properties': self._extract_properties(content),
                'dependencies': self._extract_dependencies(content),
                'complexity': self._calculate_complexity(content)
            }
            
            self.logger.info(f"Archivo analizado: {file_path.name}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error al analizar archivo {file_path}: {e}")
            raise
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extraer clases del código"""
        classes = []
        class_pattern = r'public\s+(?:abstract\s+|sealed\s+)?class\s+(\w+)(?:\s*:\s*(\w+))?'
        
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'inherits': match.group(2) if match.group(2) else None,
                'line': content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extraer métodos del código"""
        methods = []
        method_pattern = r'(public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?(\w+)\s+(\w+)\s*\([^)]*\)'
        
        for match in re.finditer(method_pattern, content):
            methods.append({
                'visibility': match.group(1),
                'return_type': match.group(2),
                'name': match.group(3),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return methods
    
    def _extract_properties(self, content: str) -> List[Dict[str, Any]]:
        """Extraer propiedades del código"""
        properties = []
        property_pattern = r'(public|private|protected|internal)\s+(\w+)\s+(\w+)\s*{\s*get;\s*set;\s*}'
        
        for match in re.finditer(property_pattern, content):
            properties.append({
                'visibility': match.group(1),
                'type': match.group(2),
                'name': match.group(3),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return properties
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extraer dependencias (using statements)"""
        using_pattern = r'using\s+([^;]+);'
        return [match.group(1).strip() for match in re.finditer(using_pattern, content)]
    
    def _calculate_complexity(self, content: str) -> int:
        """Calcular complejidad ciclomática básica"""
        complexity = 1  # Base complexity
        
        # Contar estructuras de control
        control_structures = [
            r'\bif\b', r'\belse\b', r'\bwhile\b', r'\bfor\b',
            r'\bforeach\b', r'\bswitch\b', r'\bcase\b', r'\btry\b',
            r'\bcatch\b', r'\bthrow\b'
        ]
        
        for pattern in control_structures:
            complexity += len(re.findall(pattern, content))
        
        return complexity
