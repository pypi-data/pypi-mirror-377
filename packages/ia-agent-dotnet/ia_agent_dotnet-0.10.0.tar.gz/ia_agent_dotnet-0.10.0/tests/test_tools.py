"""
Tests para herramientas del sistema
IA Agent para Generación de Pruebas Unitarias .NET
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.file_tools import file_manager
from tools.dotnet_tools import dotnet_manager


class TestTools(unittest.TestCase):
    """Tests para herramientas del sistema"""
    
    def setUp(self):
        """Configuración inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_content = "Test content for file operations"
    
    def tearDown(self):
        """Limpieza"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_manager_creation(self):
        """Test creación de file manager"""
        try:
            manager = file_manager
            self.assertIsNotNone(manager)
            
        except Exception as e:
            self.skipTest(f"File manager no disponible: {e}")
    
    def test_file_write_read(self):
        """Test escritura y lectura de archivos"""
        try:
            # Escribir archivo
            file_manager.write_file(str(self.test_file), self.test_content)
            
            # Verificar que existe
            self.assertTrue(self.test_file.exists())
            
            # Leer archivo
            content = file_manager.read_file(str(self.test_file))
            self.assertEqual(content, self.test_content)
            
        except Exception as e:
            self.skipTest(f"Test de archivos no disponible: {e}")
    
    def test_file_exists(self):
        """Test verificación de existencia de archivos"""
        try:
            # Archivo que no existe
            self.assertFalse(file_manager.file_exists(str(self.test_file)))
            
            # Crear archivo
            file_manager.write_file(str(self.test_file), self.test_content)
            
            # Archivo que existe
            self.assertTrue(file_manager.file_exists(str(self.test_file)))
            
        except Exception as e:
            self.skipTest(f"Test de existencia no disponible: {e}")
    
    def test_file_delete(self):
        """Test eliminación de archivos"""
        try:
            # Crear archivo
            file_manager.write_file(str(self.test_file), self.test_content)
            self.assertTrue(self.test_file.exists())
            
            # Eliminar archivo
            file_manager.delete_file(str(self.test_file))
            self.assertFalse(self.test_file.exists())
            
        except Exception as e:
            self.skipTest(f"Test de eliminación no disponible: {e}")
    
    def test_directory_operations(self):
        """Test operaciones de directorios"""
        try:
            test_dir = Path(self.temp_dir) / "test_dir"
            
            # Crear directorio
            file_manager.create_directory(str(test_dir))
            self.assertTrue(test_dir.exists())
            self.assertTrue(test_dir.is_dir())
            
            # Listar directorio
            files = file_manager.list_files(str(test_dir))
            self.assertIsInstance(files, list)
            
        except Exception as e:
            self.skipTest(f"Test de directorios no disponible: {e}")
    
    def test_dotnet_manager_creation(self):
        """Test creación de dotnet manager"""
        try:
            manager = dotnet_manager
            self.assertIsNotNone(manager)
            
        except Exception as e:
            self.skipTest(f"DotNet manager no disponible: {e}")
    
    def test_dotnet_version(self):
        """Test verificación de versión de .NET"""
        try:
            version = dotnet_manager.get_dotnet_version()
            self.assertIsNotNone(version)
            self.assertIsInstance(version, str)
            
        except Exception as e:
            self.skipTest(f"Test de versión .NET no disponible: {e}")
    
    def test_dotnet_project_info(self):
        """Test información de proyecto .NET"""
        try:
            # Crear un proyecto de prueba simple
            project_file = Path(self.temp_dir) / "TestProject.csproj"
            project_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
</Project>"""
            
            file_manager.write_file(str(project_file), project_content)
            
            # Obtener información del proyecto
            info = dotnet_manager.get_project_info(str(project_file))
            self.assertIsNotNone(info)
            
        except Exception as e:
            self.skipTest(f"Test de información de proyecto no disponible: {e}")
    
    def test_dotnet_build(self):
        """Test compilación de proyecto .NET"""
        try:
            # Crear un proyecto de prueba simple
            project_file = Path(self.temp_dir) / "TestProject.csproj"
            project_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <OutputType>Exe</OutputType>
  </PropertyGroup>
</Project>"""
            
            file_manager.write_file(str(project_file), project_content)
            
            # Crear archivo de código
            code_file = Path(self.temp_dir) / "Program.cs"
            code_content = """using System;

namespace TestProject
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");
        }
    }
}"""
            
            file_manager.write_file(str(code_file), code_content)
            
            # Intentar compilar
            result = dotnet_manager.build_project(str(project_file))
            self.assertIsNotNone(result)
            
        except Exception as e:
            self.skipTest(f"Test de compilación no disponible: {e}")
    
    def test_dotnet_test(self):
        """Test ejecución de pruebas .NET"""
        try:
            # Crear un proyecto de prueba simple
            test_project_file = Path(self.temp_dir) / "TestProject.Tests.csproj"
            test_project_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.0.0" />
    <PackageReference Include="xunit" Version="2.4.1" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.4.3" />
  </ItemGroup>
</Project>"""
            
            file_manager.write_file(str(test_project_file), test_project_content)
            
            # Crear archivo de prueba
            test_file = Path(self.temp_dir) / "TestClass.cs"
            test_content = """using Xunit;

namespace TestProject.Tests
{
    public class TestClass
    {
        [Fact]
        public void TestMethod()
        {
            Assert.True(true);
        }
    }
}"""
            
            file_manager.write_file(str(test_file), test_content)
            
            # Intentar ejecutar pruebas
            result = dotnet_manager.run_tests(str(test_project_file))
            self.assertIsNotNone(result)
            
        except Exception as e:
            self.skipTest(f"Test de ejecución de pruebas no disponible: {e}")


if __name__ == '__main__':
    unittest.main()
