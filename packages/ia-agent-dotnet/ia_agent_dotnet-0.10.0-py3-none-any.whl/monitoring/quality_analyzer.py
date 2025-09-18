"""
Analizador de calidad del código generado
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import ast

from utils.logging import get_logger

logger = get_logger("quality-analyzer")


@dataclass
class QualityMetrics:
    """Métricas de calidad"""
    timestamp: datetime
    code_length: int
    line_count: int
    complexity_score: float
    maintainability_score: float
    readability_score: float
    test_coverage_score: float
    overall_score: float
    issues: List[str]
    suggestions: List[str]


class QualityAnalyzer:
    """Analizador de calidad del código"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_code_quality(self, code: str, language: str = "csharp") -> QualityMetrics:
        """Analizar calidad del código"""
        try:
            # Métricas básicas
            code_length = len(code)
            line_count = len(code.split('\n'))
            
            # Análisis de complejidad
            complexity_score = self._calculate_complexity(code, language)
            
            # Análisis de mantenibilidad
            maintainability_score = self._calculate_maintainability(code, language)
            
            # Análisis de legibilidad
            readability_score = self._calculate_readability(code, language)
            
            # Análisis de cobertura de pruebas
            test_coverage_score = self._calculate_test_coverage(code, language)
            
            # Puntuación general
            overall_score = (complexity_score + maintainability_score + 
                           readability_score + test_coverage_score) / 4
            
            # Identificar problemas
            issues = self._identify_issues(code, language)
            
            # Generar sugerencias
            suggestions = self._generate_suggestions(code, language, issues)
            
            return QualityMetrics(
                timestamp=datetime.now(),
                code_length=code_length,
                line_count=line_count,
                complexity_score=complexity_score,
                maintainability_score=maintainability_score,
                readability_score=readability_score,
                test_coverage_score=test_coverage_score,
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error al analizar calidad del código: {e}")
            return QualityMetrics(
                timestamp=datetime.now(),
                code_length=0,
                line_count=0,
                complexity_score=0.0,
                maintainability_score=0.0,
                readability_score=0.0,
                test_coverage_score=0.0,
                overall_score=0.0,
                issues=[f"Error en análisis: {e}"],
                suggestions=["Revisar el código para errores de sintaxis"]
            )
    
    def _calculate_complexity(self, code: str, language: str) -> float:
        """Calcular complejidad del código"""
        try:
            if language.lower() == "csharp":
                return self._calculate_csharp_complexity(code)
            else:
                return self._calculate_generic_complexity(code)
        except Exception as e:
            self.logger.error(f"Error al calcular complejidad: {e}")
            return 0.0
    
    def _calculate_csharp_complexity(self, code: str) -> float:
        """Calcular complejidad para C#"""
        complexity = 1  # Base complexity
        
        # Contar estructuras de control
        control_structures = [
            r'\bif\b', r'\belse\b', r'\bwhile\b', r'\bfor\b',
            r'\bforeach\b', r'\bswitch\b', r'\bcase\b', r'\btry\b',
            r'\bcatch\b', r'\bthrow\b', r'\breturn\b'
        ]
        
        for pattern in control_structures:
            matches = len(re.findall(pattern, code, re.IGNORECASE))
            complexity += matches
        
        # Normalizar a escala 0-1 (invertir para que menor complejidad = mejor puntuación)
        max_complexity = 50  # Complejidad máxima esperada
        normalized_complexity = max(0, 1 - (complexity / max_complexity))
        
        return min(1.0, normalized_complexity)
    
    def _calculate_generic_complexity(self, code: str) -> float:
        """Calcular complejidad genérica"""
        # Implementación básica para otros lenguajes
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if not non_empty_lines:
            return 1.0
        
        # Métrica simple: menos líneas = mejor
        max_lines = 1000
        normalized = max(0, 1 - (len(non_empty_lines) / max_lines))
        
        return min(1.0, normalized)
    
    def _calculate_maintainability(self, code: str, language: str) -> float:
        """Calcular mantenibilidad del código"""
        try:
            score = 1.0
            
            # Verificar comentarios
            comment_ratio = self._get_comment_ratio(code, language)
            if comment_ratio < 0.1:  # Menos del 10% de comentarios
                score -= 0.2
            
            # Verificar nombres descriptivos
            descriptive_names = self._check_descriptive_names(code, language)
            if not descriptive_names:
                score -= 0.3
            
            # Verificar longitud de funciones
            long_functions = self._check_long_functions(code, language)
            if long_functions:
                score -= 0.2
            
            # Verificar duplicación
            duplication = self._check_duplication(code)
            if duplication:
                score -= 0.3
            
            return max(0.0, score)
            
        except Exception as e:
            self.logger.error(f"Error al calcular mantenibilidad: {e}")
            return 0.5
    
    def _get_comment_ratio(self, code: str, language: str) -> float:
        """Obtener ratio de comentarios"""
        if language.lower() == "csharp":
            comment_pattern = r'//.*$|/\*.*?\*/'
        else:
            comment_pattern = r'#.*$|//.*$|/\*.*?\*/'
        
        comments = re.findall(comment_pattern, code, re.MULTILINE | re.DOTALL)
        comment_chars = sum(len(comment) for comment in comments)
        total_chars = len(code)
        
        return comment_chars / total_chars if total_chars > 0 else 0
    
    def _check_descriptive_names(self, code: str, language: str) -> bool:
        """Verificar nombres descriptivos"""
        # Buscar nombres de variables y funciones
        if language.lower() == "csharp":
            name_pattern = r'(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?\w+\s+(\w+)\s*\('
        else:
            name_pattern = r'def\s+(\w+)\s*\('
        
        names = re.findall(name_pattern, code)
        
        # Verificar que los nombres sean descriptivos (más de 3 caracteres)
        descriptive_names = [name for name in names if len(name) > 3]
        
        return len(descriptive_names) / len(names) > 0.7 if names else True
    
    def _check_long_functions(self, code: str, language: str) -> bool:
        """Verificar funciones largas"""
        lines = code.split('\n')
        in_function = False
        function_lines = 0
        max_function_lines = 50
        
        for line in lines:
            if re.search(r'(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?\w+\s+\w+\s*\(', line):
                if in_function and function_lines > max_function_lines:
                    return True
                in_function = True
                function_lines = 0
            elif in_function:
                if line.strip() and not line.strip().startswith('//'):
                    function_lines += 1
                if line.strip() == '}':
                    in_function = False
        
        return False
    
    def _check_duplication(self, code: str) -> bool:
        """Verificar duplicación de código"""
        lines = [line.strip() for line in code.split('\n') if line.strip() and not line.strip().startswith('//')]
        
        # Buscar líneas duplicadas
        line_counts = {}
        for line in lines:
            line_counts[line] = line_counts.get(line, 0) + 1
        
        # Si hay muchas líneas duplicadas, es problemático
        duplicates = sum(count for count in line_counts.values() if count > 1)
        return duplicates > len(lines) * 0.1  # Más del 10% de duplicación
    
    def _calculate_readability(self, code: str, language: str) -> float:
        """Calcular legibilidad del código"""
        try:
            score = 1.0
            
            # Verificar indentación consistente
            if not self._check_consistent_indentation(code):
                score -= 0.2
            
            # Verificar espaciado
            if not self._check_proper_spacing(code):
                score -= 0.2
            
            # Verificar longitud de líneas
            long_lines = self._check_long_lines(code)
            if long_lines:
                score -= 0.3
            
            # Verificar estructura
            if not self._check_proper_structure(code, language):
                score -= 0.3
            
            return max(0.0, score)
            
        except Exception as e:
            self.logger.error(f"Error al calcular legibilidad: {e}")
            return 0.5
    
    def _check_consistent_indentation(self, code: str) -> bool:
        """Verificar indentación consistente"""
        lines = [line for line in code.split('\n') if line.strip()]
        
        if not lines:
            return True
        
        # Verificar que todas las líneas usen la misma indentación
        indentations = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indentations.append(indent)
        
        # Verificar consistencia
        if not indentations:
            return True
        
        # Debe ser múltiplo de 2 o 4
        base_indent = min(indentations)
        for indent in indentations:
            if (indent - base_indent) % 4 != 0 and (indent - base_indent) % 2 != 0:
                return False
        
        return True
    
    def _check_proper_spacing(self, code: str) -> bool:
        """Verificar espaciado apropiado"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Verificar espacios alrededor de operadores
            if re.search(r'[a-zA-Z0-9][=+\-*/][a-zA-Z0-9]', line):
                return False
            
            # Verificar espacios después de comas
            if re.search(r',[a-zA-Z0-9]', line):
                return False
        
        return True
    
    def _check_long_lines(self, code: str) -> bool:
        """Verificar líneas largas"""
        lines = code.split('\n')
        max_line_length = 120
        
        long_lines = [line for line in lines if len(line) > max_line_length]
        return len(long_lines) > len(lines) * 0.1  # Más del 10% de líneas largas
    
    def _check_proper_structure(self, code: str, language: str) -> bool:
        """Verificar estructura apropiada"""
        if language.lower() == "csharp":
            # Verificar que tenga namespace, class, etc.
            has_namespace = 'namespace' in code
            has_class = 'class' in code
            return has_namespace and has_class
        else:
            return True
    
    def _calculate_test_coverage(self, code: str, language: str) -> float:
        """Calcular cobertura de pruebas"""
        try:
            if language.lower() == "csharp":
                # Buscar métodos públicos
                public_methods = re.findall(r'public\s+(?:static\s+)?(?:async\s+)?\w+\s+(\w+)\s*\(', code)
                
                # Buscar pruebas
                test_methods = re.findall(r'\[(?:Fact|Test|TestMethod)\].*?public\s+\w+\s+(\w+)\s*\(', code, re.DOTALL)
                
                if not public_methods:
                    return 1.0  # No hay métodos públicos que probar
                
                coverage = len(test_methods) / len(public_methods)
                return min(1.0, coverage)
            else:
                return 0.5  # Valor por defecto para otros lenguajes
                
        except Exception as e:
            self.logger.error(f"Error al calcular cobertura de pruebas: {e}")
            return 0.0
    
    def _identify_issues(self, code: str, language: str) -> List[str]:
        """Identificar problemas en el código"""
        issues = []
        
        # Verificar problemas comunes
        if not self._check_descriptive_names(code, language):
            issues.append("Nombres de variables/funciones no descriptivos")
        
        if self._check_long_functions(code, language):
            issues.append("Funciones demasiado largas")
        
        if self._check_duplication(code):
            issues.append("Código duplicado detectado")
        
        if not self._check_consistent_indentation(code):
            issues.append("Indentación inconsistente")
        
        if not self._check_proper_spacing(code):
            issues.append("Espaciado inapropiado")
        
        if self._check_long_lines(code):
            issues.append("Líneas demasiado largas")
        
        if not self._check_proper_structure(code, language):
            issues.append("Estructura de código inapropiada")
        
        return issues
    
    def _generate_suggestions(self, code: str, language: str, issues: List[str]) -> List[str]:
        """Generar sugerencias de mejora"""
        suggestions = []
        
        if "Nombres de variables/funciones no descriptivos" in issues:
            suggestions.append("Usar nombres más descriptivos para variables y funciones")
        
        if "Funciones demasiado largas" in issues:
            suggestions.append("Dividir funciones largas en funciones más pequeñas")
        
        if "Código duplicado detectado" in issues:
            suggestions.append("Extraer código duplicado a funciones reutilizables")
        
        if "Indentación inconsistente" in issues:
            suggestions.append("Usar indentación consistente (2 o 4 espacios)")
        
        if "Espaciado inapropiado" in issues:
            suggestions.append("Agregar espacios alrededor de operadores y después de comas")
        
        if "Líneas demasiado largas" in issues:
            suggestions.append("Dividir líneas largas en múltiples líneas")
        
        if "Estructura de código inapropiada" in issues:
            suggestions.append("Organizar código en namespaces y clases apropiadas")
        
        if not suggestions:
            suggestions.append("El código tiene buena calidad general")
        
        return suggestions
