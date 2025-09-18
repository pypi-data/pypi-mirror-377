# IA Agent para Generación de Pruebas Unitarias .NET

[![PyPI version](https://badge.fury.io/py/ia-agent-dotnet.svg)](https://badge.fury.io/py/ia-agent-dotnet)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![.NET 8.0+](https://img.shields.io/badge/.NET-8.0+-purple.svg)](https://dotnet.microsoft.com/download)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un sistema multi-agente de IA avanzado con capacidades de memoria y herramientas externas (ReAct) especializado en la generación automática de pruebas unitarias para APIs REST desarrolladas en .NET.

## 🚀 Instalación Rápida

```bash
# Instalar desde PyPI
pip install ia-agent-dotnet

# Configurar el agente (una sola vez)
ia-agent-config

# ¡Listo para usar! (Descubre proyectos automáticamente)
ia-agent
```

## 🚀 Características Principales

- **🤖 Sistema Multi-Agente**: Colaboración inteligente entre agentes especializados
- **🔍 Descubrimiento Automático**: Detecta proyectos .NET automáticamente en el directorio actual
- **🎯 Selección Interactiva**: Interfaz amigable para seleccionar proyectos
- **🧠 Memoria Persistente**: Recuerda conversaciones y contexto entre sesiones
- **🛠️ Herramientas Externas**: Ejecuta código y busca documentación automáticamente
- **🔄 Patrón ReAct**: Razonamiento y actuación iterativa para decisiones autónomas
- **🎯 Especialización**: Agentes especializados en análisis, generación, validación y optimización
- **📊 Soporte Multi-Framework**: xUnit, NUnit, MSTest
- **⚡ CLI Interactivo Persistente**: Interfaz de línea de comandos que mantiene el estado entre comandos
- **🔧 Configuración Global**: Sistema de configuración centralizado para API keys
- **✅ Validación Automática**: Verificación de configuración y versiones al inicio
- **🎨 Interfaz Mejorada**: Tablas y paneles con información detallada de análisis
- **🔄 Recarga Dinámica**: Actualización automática de configuración sin reiniciar

## 🏗️ Arquitectura

El sistema utiliza **LangChain** para capacidades ReAct individuales y **AutoGen** para colaboración entre agentes especializados:

- **Agente Analista**: Analiza código .NET y extrae información
- **Agente Generador**: Genera código de pruebas y templates
- **Agente Validador**: Valida código y ejecuta pruebas
- **Agente Optimizador**: Optimiza pruebas y sugiere mejoras
- **Agente Coordinador**: Coordina tareas y gestiona flujos de trabajo

## 🆕 Nuevas Funcionalidades (v0.8.0)

### CLI Interactivo Persistente
- **Estado Persistente**: Los agentes se cargan una sola vez y mantienen el estado entre comandos
- **Comandos Rápidos**: Ejecuta `analyze`, `generate`, `validate` sin reinicializar
- **Interfaz Mejorada**: Tablas con métricas detalladas y paneles informativos
- **Validación Automática**: Verifica configuración y versiones al inicio

### Sistema de Configuración Global
- **Configuración Centralizada**: API keys almacenadas globalmente
- **Recarga Dinámica**: Actualiza configuración sin reiniciar la aplicación
- **Validación Inteligente**: Detecta claves válidas vs placeholders
- **Soporte Multi-Proveedor**: DeepSeek, Gemini 2.5, OpenAI

### Mejoras en Análisis
- **Métricas Detalladas**: Contadores de controladores, modelos, servicios
- **Extracción Inteligente**: Parsea automáticamente resultados del agente
- **Presentación Visual**: Tablas y paneles con información estructurada

## 🔧 Configuración

### Configuración Global (Recomendado)
```bash
# Configurar el agente una sola vez
ia-agent-config

# Ver configuración actual
ia-agent-config --status
```

### Proveedores de IA Disponibles
- **DeepSeek** (Recomendado) - Especializado en programación, más económico
- **Gemini** - Google AI, bueno para análisis general  
- **OpenAI** - Estándar de la industria, más caro

> 💡 **Nota**: La configuración se guarda globalmente y se aplica a todos tus proyectos. No necesitas archivos `.env` en cada proyecto.

## 🎯 Uso Básico

### Comandos Principales
```bash
# Descubrir y analizar proyectos automáticamente (NUEVO)
ia-agent

# Ver ayuda del agente
ia-agent --help

# Analizar un proyecto específico (opcional)
ia-agent --project-path ./mi-proyecto

# Configurar el agente
ia-agent-config

# Ver estado de configuración
ia-agent-config --status
```

### Ejemplos de Uso
```bash
# Descubrir proyectos en directorio actual (RECOMENDADO)
ia-agent

# Analizar proyecto específico
ia-agent --project-path ./src/MyProject

# Ver logs detallados
ia-agent --log-level DEBUG
```

### 🔍 Descubrimiento Automático de Proyectos

El agente ahora detecta automáticamente todos los proyectos .NET en el directorio actual:

```bash
# Navega a tu directorio de proyecto
cd ./mi-proyecto-dotnet

# Ejecuta el agente (descubre automáticamente)
ia-agent
```

**El agente mostrará:**
- 📁 Lista de proyectos .NET encontrados
- 🎯 Tipo de proyecto (Web API, Console, Library, Test)
- 🔧 Framework objetivo (.NET 8.0, etc.)
- 📦 Paquetes NuGet utilizados
- 🎯 Opción de selección interactiva

## 📋 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11 (64-bit), Linux, macOS
- **Python**: 3.11 o superior
- **.NET SDK**: 8.0 o superior (para proyectos .NET)
- **Memoria RAM**: 8GB mínimo, 16GB recomendado
- **Conexión a Internet**: Para APIs de IA
- **API Key**: DeepSeek, Gemini o OpenAI

## 📚 Documentación

- [📖 Guía de Usuario](docs/USER_GUIDE.md)
- [🔧 Guía de Desarrollador](docs/DEVELOPER_GUIDE.md)
- [🚀 Guía de Despliegue](docs/DEPLOYMENT_GUIDE.md)
- [🏗️ Arquitectura del Sistema](docs/architecture.md)
- [🔍 Referencia de API](docs/API_REFERENCE.md)
- [❓ Solución de Problemas](docs/TROUBLESHOOTING.md)

## 🛠️ Desarrollo

### Instalación para Desarrollo
```bash
# Clonar el repositorio
git clone https://github.com/Lopand-Solutions/ia-agent-to-unit-test-api-rest.git
cd ia-agent-to-unit-test-api-rest

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar en modo desarrollo
pip install -e .
```

### Contribuir
1. Fork el repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📊 Estado del Proyecto

### ✅ Fases Completadas

#### Fase 1: Análisis y Diseño ✅
- [x] Estructura del proyecto creada
- [x] Dependencias configuradas
- [x] Repositorio Git inicializado
- [x] Archivos de configuración creados
- [x] Requisitos documentados
- [x] Arquitectura diseñada

#### Fase 2: Desarrollo del Sistema Multi-Agente ✅
- [x] Agentes especializados implementados
- [x] Sistema de memoria vectorial
- [x] Herramientas .NET integradas
- [x] CLI básico funcional
- [x] Sistema de logging implementado

#### Fase 3: Funcionalidades Avanzadas ✅
- [x] Suite de testing completa
- [x] Mejoras de IA implementadas
- [x] Sistema de monitoreo
- [x] Documentación de API
- [x] Optimizaciones de rendimiento

#### Fase 4: Optimización y Despliegue ✅
- [x] Sistema de configuración robusto
- [x] Manager de memoria optimizado
- [x] Optimizador de rendimiento
- [x] Manejador de errores avanzado
- [x] Configuración Docker completa
- [x] Scripts de despliegue automatizado
- [x] Validador de producción

#### Fase 5: Documentación Final y Entrega ✅
- [x] Guía de usuario completa
- [x] Guía de desarrollador
- [x] Guía de despliegue
- [x] Documentación de API
- [x] Guía de solución de problemas
- [x] Changelog del proyecto
- [x] Licencia MIT

### 🎯 Versión Actual: v0.7.0
- **Estado**: ✅ **DISPONIBLE EN PyPI**
- **Funcionalidades**: Sistema multi-agente con descubrimiento automático de proyectos
- **Nuevo**: 🔍 Descubrimiento automático y selección interactiva de proyectos .NET
- **Configuración**: Global y automática (sin archivos .env)
- **Proveedores**: DeepSeek, Gemini, OpenAI
- **Documentación**: Guías completas y API reference

## 🤝 Soporte

- **GitHub Issues**: [Reportar bugs y solicitar features](https://github.com/Lopand-Solutions/ia-agent-to-unit-test-api-rest/issues)
- **Documentación**: Guías completas en el directorio `docs/`
- **PyPI**: [ia-agent-dotnet](https://pypi.org/project/ia-agent-dotnet/)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [LangChain](https://langchain.com/) - Framework para agentes con capacidades ReAct
- [AutoGen](https://microsoft.github.io/autogen/) - Framework para colaboración multi-agente
- [DeepSeek](https://platform.deepseek.com/) - IA especializada en programación
- [Google Gemini](https://makersuite.google.com/) - Google AI para análisis general
- [OpenAI](https://openai.com/) - APIs de IA para generación de código
- Comunidad .NET por las mejores prácticas de testing

---

**Desarrollado con ❤️ para la comunidad .NET**

[![PyPI version](https://badge.fury.io/py/ia-agent-dotnet.svg)](https://badge.fury.io/py/ia-agent-dotnet)
[![GitHub](https://img.shields.io/github/stars/Lopand-Solutions/ia-agent-to-unit-test-api-rest?style=social)](https://github.com/Lopand-Solutions/ia-agent-to-unit-test-api-rest)