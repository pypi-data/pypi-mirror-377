"""
Ingeniero de prompts avanzado
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

from utils.logging import get_logger

logger = get_logger("prompt-engineer")


class PromptType(Enum):
    """Tipos de prompts"""
    CODE_ANALYSIS = "code_analysis"
    TEST_GENERATION = "test_generation"
    CODE_OPTIMIZATION = "code_optimization"
    DOCUMENTATION = "documentation"
    EXPLANATION = "explanation"


@dataclass
class PromptTemplate:
    """Template de prompt"""
    name: str
    type: PromptType
    template: str
    variables: List[str]
    description: str


class PromptEngineer:
    """Ingeniero de prompts para optimizar interacciones con LLM"""
    
    def __init__(self):
        self.logger = logger
        self.templates = {}
        self._setup_default_templates()
    
    def _setup_default_templates(self):
        """Configurar templates por defecto"""
        try:
            # Template para análisis de código
            self.templates["code_analysis"] = PromptTemplate(
                name="code_analysis",
                type=PromptType.CODE_ANALYSIS,
                template="""
Eres un experto analista de código .NET. Analiza el siguiente código y proporciona un análisis detallado:

**Código a analizar:**
```csharp
{code}
```

**Contexto del proyecto:**
{context}

**Instrucciones de análisis:**
1. **Estructura y arquitectura**: Identifica patrones de diseño, arquitectura y organización
2. **Calidad del código**: Evalúa legibilidad, mantenibilidad y mejores prácticas
3. **Dependencias**: Identifica dependencias externas e internas
4. **Complejidad**: Calcula complejidad ciclomática y identifica áreas complejas
5. **Seguridad**: Identifica posibles vulnerabilidades de seguridad
6. **Rendimiento**: Identifica posibles problemas de rendimiento
7. **Recomendaciones**: Proporciona sugerencias específicas de mejora

**Formato de respuesta:**
```json
{{
    "structure": {{
        "patterns": ["patrón1", "patrón2"],
        "architecture": "descripción",
        "organization": "evaluación"
    }},
    "quality": {{
        "readability": "evaluación",
        "maintainability": "evaluación",
        "best_practices": ["práctica1", "práctica2"]
    }},
    "dependencies": {{
        "external": ["dep1", "dep2"],
        "internal": ["dep1", "dep2"]
    }},
    "complexity": {{
        "cyclomatic": número,
        "areas": ["área1", "área2"]
    }},
    "security": {{
        "vulnerabilities": ["vuln1", "vuln2"],
        "recommendations": ["rec1", "rec2"]
    }},
    "performance": {{
        "issues": ["issue1", "issue2"],
        "optimizations": ["opt1", "opt2"]
    }},
    "recommendations": [
        "recomendación específica 1",
        "recomendación específica 2"
    ]
}}
```

Proporciona un análisis completo y detallado.
""",
                variables=["code", "context"],
                description="Template para análisis detallado de código .NET"
            )
            
            # Template para generación de pruebas
            self.templates["test_generation"] = PromptTemplate(
                name="test_generation",
                type=PromptType.TEST_GENERATION,
                template="""
Eres un experto en testing de código .NET. Genera pruebas unitarias completas y de alta calidad.

**Código a probar:**
```csharp
{code}
```

**Análisis previo:**
{analysis}

**Framework de testing:** {framework}

**Instrucciones de generación:**
1. **Cobertura completa**: Genera pruebas para todos los métodos públicos
2. **Casos de prueba**: Incluye casos normales, edge cases y casos de error
3. **Mocks y stubs**: Usa mocks apropiados para dependencias
4. **Assertions**: Incluye assertions específicas y descriptivas
5. **Nomenclatura**: Usa nomenclatura clara y descriptiva
6. **Documentación**: Incluye comentarios explicativos
7. **Mejores prácticas**: Sigue las mejores prácticas del framework

**Formato de respuesta:**
```csharp
using {framework_using};
using Moq;
using {namespace};

namespace {namespace}.Tests
{{
    public class {class_name}Tests
    {{
        // Arrange
        private {class_name} _sut;
        private Mock<{dependency_type}> _mockDependency;
        
        public {class_name}Tests()
        {{
            _mockDependency = new Mock<{dependency_type}>();
            _sut = new {class_name}(_mockDependency.Object);
        }}
        
        [Fact]
        public void {method_name}_WithValidInput_ShouldReturnExpectedResult()
        {{
            // Arrange
            var input = "test_input";
            var expected = "expected_result";
            
            // Act
            var result = _sut.{method_name}(input);
            
            // Assert
            Assert.Equal(expected, result);
        }}
        
        // Más pruebas...
    }}
}}
```

Genera pruebas completas, bien estructuradas y de alta calidad.
""",
                variables=["code", "analysis", "framework", "framework_using", "namespace", "class_name", "dependency_type", "method_name"],
                description="Template para generación de pruebas unitarias"
            )
            
            # Template para optimización de código
            self.templates["code_optimization"] = PromptTemplate(
                name="code_optimization",
                type=PromptType.CODE_OPTIMIZATION,
                template="""
Eres un experto en optimización de código .NET. Optimiza el siguiente código para mejorar rendimiento, legibilidad y mantenibilidad.

**Código original:**
```csharp
{code}
```

**Análisis previo:**
{analysis}

**Instrucciones de optimización:**
1. **Rendimiento**: Optimiza algoritmos, reduce complejidad, mejora eficiencia
2. **Legibilidad**: Mejora nombres, estructura y organización
3. **Mantenibilidad**: Reduce acoplamiento, aumenta cohesión
4. **Mejores prácticas**: Aplica patrones y principios SOLID
5. **Seguridad**: Mejora manejo de errores y validaciones
6. **Documentación**: Agrega documentación apropiada

**Formato de respuesta:**
```csharp
// Código optimizado
{optimized_code}

// Explicación de cambios:
{explanation}

// Beneficios:
{benefits}
```

Proporciona código optimizado con explicaciones detalladas.
""",
                variables=["code", "analysis"],
                description="Template para optimización de código"
            )
            
            self.logger.info("Templates de prompts configurados")
            
        except Exception as e:
            self.logger.error(f"Error al configurar templates: {e}")
            raise
    
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Obtener template por nombre"""
        return self.templates.get(template_name)
    
    def generate_prompt(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Generar prompt desde template"""
        try:
            template = self.get_template(template_name)
            if not template:
                raise ValueError(f"Template '{template_name}' no encontrado")
            
            # Verificar que todas las variables requeridas estén presentes
            missing_vars = [var for var in template.variables if var not in variables]
            if missing_vars:
                raise ValueError(f"Variables faltantes: {missing_vars}")
            
            # Generar prompt
            prompt = template.template.format(**variables)
            
            self.logger.info(f"Prompt generado desde template: {template_name}")
            return prompt
            
        except Exception as e:
            self.logger.error(f"Error al generar prompt: {e}")
            raise
    
    def get_available_templates(self) -> List[str]:
        """Obtener templates disponibles"""
        return list(self.templates.keys())
    
    def add_custom_template(self, template: PromptTemplate):
        """Agregar template personalizado"""
        self.templates[template.name] = template
        self.logger.info(f"Template personalizado agregado: {template.name}")
    
    def optimize_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Optimizar prompt existente"""
        try:
            # Agregar contexto relevante
            optimized = f"""
**Contexto del proyecto:**
- Framework: {context.get('framework', 'N/A')}
- Versión .NET: {context.get('dotnet_version', 'N/A')}
- Patrones utilizados: {', '.join(context.get('patterns', []))}
- Dependencias principales: {', '.join(context.get('dependencies', []))}

{prompt}

**Instrucciones adicionales:**
- Mantén consistencia con el estilo del proyecto
- Considera las limitaciones del framework
- Prioriza la claridad y mantenibilidad
"""
            
            return optimized
            
        except Exception as e:
            self.logger.error(f"Error al optimizar prompt: {e}")
            return prompt
