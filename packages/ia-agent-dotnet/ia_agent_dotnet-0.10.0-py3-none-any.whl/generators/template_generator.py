"""
Generador de templates
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import os

from utils.logging import get_logger

logger = get_logger("template-generator")


class TemplateGenerator:
    """Generador de templates"""
    
    def __init__(self, templates_path: Path = Path("templates")):
        self.templates_path = templates_path
        self.logger = logger
    
    def load_template(self, template_name: str, framework: str = "xunit") -> str:
        """Cargar template desde archivo"""
        try:
            template_file = self.templates_path / framework / f"{template_name}.cs"
            
            if not template_file.exists():
                self.logger.warning(f"Template no encontrado: {template_file}")
                return self._get_default_template(template_name, framework)
            
            content = template_file.read_text(encoding='utf-8')
            self.logger.info(f"Template cargado: {template_name}")
            return content
            
        except Exception as e:
            self.logger.error(f"Error al cargar template {template_name}: {e}")
            return self._get_default_template(template_name, framework)
    
    def generate_from_template(self, template_name: str, variables: Dict[str, Any], framework: str = "xunit") -> str:
        """Generar código desde template con variables"""
        try:
            template = self.load_template(template_name, framework)
            
            # Reemplazar variables en el template
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                template = template.replace(placeholder, str(value))
            
            self.logger.info(f"Código generado desde template: {template_name}")
            return template
            
        except Exception as e:
            self.logger.error(f"Error al generar desde template {template_name}: {e}")
            raise
    
    def _get_default_template(self, template_name: str, framework: str) -> str:
        """Obtener template por defecto"""
        if template_name == "test_class":
            return self._get_default_test_class_template(framework)
        elif template_name == "test_method":
            return self._get_default_test_method_template(framework)
        else:
            return "// Template no encontrado"
    
    def _get_default_test_class_template(self, framework: str) -> str:
        """Template por defecto para clase de prueba"""
        if framework == "xunit":
            return """using Xunit;
using Moq;

namespace {namespace}
{
    public class {class_name}Tests
    {
        [Fact]
        public void {method_name}_ShouldReturnExpectedResult()
        {
            // Arrange
            var sut = new {class_name}();
            
            // Act
            var result = sut.{method_name}();
            
            // Assert
            Assert.NotNull(result);
        }
    }
}"""
        elif framework == "nunit":
            return """using NUnit.Framework;
using Moq;

namespace {namespace}
{
    [TestFixture]
    public class {class_name}Tests
    {
        [Test]
        public void {method_name}_ShouldReturnExpectedResult()
        {
            // Arrange
            var sut = new {class_name}();
            
            // Act
            var result = sut.{method_name}();
            
            // Assert
            Assert.That(result, Is.Not.Null);
        }
    }
}"""
        else:  # mstest
            return """using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;

namespace {namespace}
{
    [TestClass]
    public class {class_name}Tests
    {
        [TestMethod]
        public void {method_name}_ShouldReturnExpectedResult()
        {
            // Arrange
            var sut = new {class_name}();
            
            // Act
            var result = sut.{method_name}();
            
            // Assert
            Assert.IsNotNull(result);
        }
    }
}"""
    
    def _get_default_test_method_template(self, framework: str) -> str:
        """Template por defecto para método de prueba"""
        if framework == "xunit":
            return """[Fact]
public void {method_name}_ShouldReturnExpectedResult()
{
    // Arrange
    var sut = new {class_name}();
    
    // Act
    var result = sut.{method_name}();
    
    // Assert
    Assert.NotNull(result);
}"""
        elif framework == "nunit":
            return """[Test]
public void {method_name}_ShouldReturnExpectedResult()
{
    // Arrange
    var sut = new {class_name}();
    
    // Act
    var result = sut.{method_name}();
    
    // Assert
    Assert.That(result, Is.Not.Null);
}"""
        else:  # mstest
            return """[TestMethod]
public void {method_name}_ShouldReturnExpectedResult()
{
    // Arrange
    var sut = new {class_name}();
    
    // Act
    var result = sut.{method_name}();
    
    // Assert
    Assert.IsNotNull(result);
}"""
