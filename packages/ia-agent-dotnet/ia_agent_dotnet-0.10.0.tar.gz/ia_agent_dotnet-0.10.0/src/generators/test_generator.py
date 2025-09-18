"""
Generador de pruebas unitarias
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum

from utils.logging import get_logger

logger = get_logger("test-generator")


class TestFramework(Enum):
    """Frameworks de testing soportados"""
    XUNIT = "xunit"
    NUNIT = "nunit"
    MSTEST = "mstest"


class TestGenerator:
    """Generador de pruebas unitarias"""
    
    def __init__(self, framework: TestFramework = TestFramework.XUNIT):
        self.framework = framework
        self.logger = logger
    
    def generate_test(self, class_info: Dict[str, Any], method_info: Dict[str, Any]) -> str:
        """Generar prueba unitaria para un método"""
        try:
            if self.framework == TestFramework.XUNIT:
                return self._generate_xunit_test(class_info, method_info)
            elif self.framework == TestFramework.NUNIT:
                return self._generate_nunit_test(class_info, method_info)
            elif self.framework == TestFramework.MSTEST:
                return self._generate_mstest_test(class_info, method_info)
            else:
                raise ValueError(f"Framework no soportado: {self.framework}")
                
        except Exception as e:
            self.logger.error(f"Error al generar prueba: {e}")
            raise
    
    def _generate_xunit_test(self, class_info: Dict[str, Any], method_info: Dict[str, Any]) -> str:
        """Generar prueba con xUnit"""
        class_name = class_info.get('name', 'UnknownClass')
        method_name = method_info.get('name', 'UnknownMethod')
        
        test_code = f"""using Xunit;
using Moq;
using {class_info.get('namespace', 'YourNamespace')};

namespace {class_info.get('namespace', 'YourNamespace')}.Tests
{{
    public class {class_name}Tests
    {{
        [Fact]
        public void {method_name}_ShouldReturnExpectedResult()
        {{
            // Arrange
            var sut = new {class_name}();
            
            // Act
            var result = sut.{method_name}();
            
            // Assert
            Assert.NotNull(result);
        }}
        
        [Theory]
        [InlineData("test")]
        public void {method_name}_WithValidInput_ShouldReturnExpectedResult(string input)
        {{
            // Arrange
            var sut = new {class_name}();
            
            // Act
            var result = sut.{method_name}(input);
            
            // Assert
            Assert.NotNull(result);
        }}
    }}
}}"""
        
        return test_code
    
    def _generate_nunit_test(self, class_info: Dict[str, Any], method_info: Dict[str, Any]) -> str:
        """Generar prueba con NUnit"""
        class_name = class_info.get('name', 'UnknownClass')
        method_name = method_info.get('name', 'UnknownMethod')
        
        test_code = f"""using NUnit.Framework;
using Moq;
using {class_info.get('namespace', 'YourNamespace')};

namespace {class_info.get('namespace', 'YourNamespace')}.Tests
{{
    [TestFixture]
    public class {class_name}Tests
    {{
        [Test]
        public void {method_name}_ShouldReturnExpectedResult()
        {{
            // Arrange
            var sut = new {class_name}();
            
            // Act
            var result = sut.{method_name}();
            
            // Assert
            Assert.That(result, Is.Not.Null);
        }}
        
        [TestCase("test")]
        public void {method_name}_WithValidInput_ShouldReturnExpectedResult(string input)
        {{
            // Arrange
            var sut = new {class_name}();
            
            // Act
            var result = sut.{method_name}(input);
            
            // Assert
            Assert.That(result, Is.Not.Null);
        }}
    }}
}}"""
        
        return test_code
    
    def _generate_mstest_test(self, class_info: Dict[str, Any], method_info: Dict[str, Any]) -> str:
        """Generar prueba con MSTest"""
        class_name = class_info.get('name', 'UnknownClass')
        method_name = method_info.get('name', 'UnknownMethod')
        
        test_code = f"""using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using {class_info.get('namespace', 'YourNamespace')};

namespace {class_info.get('namespace', 'YourNamespace')}.Tests
{{
    [TestClass]
    public class {class_name}Tests
    {{
        [TestMethod]
        public void {method_name}_ShouldReturnExpectedResult()
        {{
            // Arrange
            var sut = new {class_name}();
            
            // Act
            var result = sut.{method_name}();
            
            // Assert
            Assert.IsNotNull(result);
        }}
        
        [DataTestMethod]
        [DataRow("test")]
        public void {method_name}_WithValidInput_ShouldReturnExpectedResult(string input)
        {{
            // Arrange
            var sut = new {class_name}();
            
            // Act
            var result = sut.{method_name}(input);
            
            // Assert
            Assert.IsNotNull(result);
        }}
    }}
}}"""
        
        return test_code
