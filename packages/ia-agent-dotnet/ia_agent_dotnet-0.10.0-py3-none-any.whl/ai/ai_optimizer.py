"""
Optimizador de IA para mejorar rendimiento y calidad
IA Agent para Generación de Pruebas Unitarias .NET
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
import time

from utils.logging import get_logger

logger = get_logger("ai-optimizer")


@dataclass
class OptimizationMetrics:
    """Métricas de optimización"""
    response_time: float
    token_count: int
    quality_score: float
    cost_estimate: float
    timestamp: datetime


@dataclass
class OptimizationResult:
    """Resultado de optimización"""
    original_response: str
    optimized_response: str
    improvements: List[str]
    metrics: OptimizationMetrics


class AIOptimizer:
    """Optimizador de IA para mejorar rendimiento y calidad"""
    
    def __init__(self):
        self.logger = logger
        self.metrics_history: List[OptimizationMetrics] = []
        self.optimization_rules = self._setup_optimization_rules()
    
    def _setup_optimization_rules(self) -> Dict[str, Any]:
        """Configurar reglas de optimización"""
        return {
            "prompt_optimization": {
                "max_length": 4000,
                "include_context": True,
                "use_examples": True,
                "clear_instructions": True
            },
            "response_optimization": {
                "max_length": 6000,
                "structured_output": True,
                "include_explanations": True,
                "quality_checks": True
            },
            "performance_optimization": {
                "timeout": 30,
                "retry_attempts": 3,
                "batch_processing": True,
                "caching": True
            }
        }
    
    async def optimize_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Optimizar prompt para mejor rendimiento"""
        try:
            start_time = time.time()
            
            # Aplicar reglas de optimización
            optimized_prompt = self._apply_prompt_optimization(prompt, context)
            
            # Medir métricas
            optimization_time = time.time() - start_time
            
            self.logger.info(f"Prompt optimizado en {optimization_time:.2f}s")
            return optimized_prompt
            
        except Exception as e:
            self.logger.error(f"Error al optimizar prompt: {e}")
            return prompt
    
    def _apply_prompt_optimization(self, prompt: str, context: Dict[str, Any]) -> str:
        """Aplicar optimizaciones al prompt"""
        optimized = prompt
        
        # Agregar contexto relevante si no está presente
        if "context" not in optimized.lower() and context:
            context_section = "\n\n**Contexto adicional:**\n"
            for key, value in context.items():
                context_section += f"- {key}: {value}\n"
            optimized += context_section
        
        # Agregar ejemplos si no están presentes
        if "ejemplo" not in optimized.lower() and "example" not in optimized.lower():
            optimized += "\n\n**Ejemplo de respuesta esperada:**\nProporciona una respuesta estructurada y detallada."
        
        # Limitar longitud si es necesario
        max_length = self.optimization_rules["prompt_optimization"]["max_length"]
        if len(optimized) > max_length:
            optimized = optimized[:max_length] + "\n\n[Prompt truncado para optimización]"
        
        return optimized
    
    async def optimize_response(self, response: str, prompt: str) -> OptimizationResult:
        """Optimizar respuesta del LLM"""
        try:
            start_time = time.time()
            
            # Analizar respuesta original
            original_metrics = self._analyze_response(response)
            
            # Aplicar optimizaciones
            optimized_response = self._apply_response_optimization(response, prompt)
            
            # Analizar respuesta optimizada
            optimized_metrics = self._analyze_response(optimized_response)
            
            # Identificar mejoras
            improvements = self._identify_improvements(original_metrics, optimized_metrics)
            
            # Crear resultado
            result = OptimizationResult(
                original_response=response,
                optimized_response=optimized_response,
                improvements=improvements,
                metrics=OptimizationMetrics(
                    response_time=time.time() - start_time,
                    token_count=len(optimized_response.split()),
                    quality_score=self._calculate_quality_score(optimized_response),
                    cost_estimate=self._estimate_cost(optimized_response),
                    timestamp=datetime.now()
                )
            )
            
            # Guardar métricas
            self.metrics_history.append(result.metrics)
            
            self.logger.info(f"Respuesta optimizada con {len(improvements)} mejoras")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al optimizar respuesta: {e}")
            # Retornar respuesta original en caso de error
            return OptimizationResult(
                original_response=response,
                optimized_response=response,
                improvements=[],
                metrics=OptimizationMetrics(
                    response_time=0,
                    token_count=len(response.split()),
                    quality_score=0.5,
                    cost_estimate=0,
                    timestamp=datetime.now()
                )
            )
    
    def _apply_response_optimization(self, response: str, prompt: str) -> str:
        """Aplicar optimizaciones a la respuesta"""
        optimized = response
        
        # Mejorar estructura si es código
        if "```" in response:
            optimized = self._improve_code_structure(optimized)
        
        # Agregar explicaciones si faltan
        if "explicación" not in optimized.lower() and "explanation" not in optimized.lower():
            optimized += "\n\n**Explicación:** Esta respuesta ha sido optimizada para mayor claridad y utilidad."
        
        # Limpiar formato
        optimized = self._clean_formatting(optimized)
        
        return optimized
    
    def _improve_code_structure(self, response: str) -> str:
        """Mejorar estructura del código en la respuesta"""
        # Agregar comentarios explicativos si faltan
        if "//" not in response and "#" not in response:
            lines = response.split('\n')
            improved_lines = []
            
            for line in lines:
                if line.strip().startswith('public') or line.strip().startswith('private'):
                    improved_lines.append(f"    // {line.strip()}")
                improved_lines.append(line)
            
            response = '\n'.join(improved_lines)
        
        return response
    
    def _clean_formatting(self, response: str) -> str:
        """Limpiar formato de la respuesta"""
        # Remover espacios extra
        lines = [line.rstrip() for line in response.split('\n')]
        
        # Remover líneas vacías excesivas
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            if line.strip() == "":
                if not prev_empty:
                    cleaned_lines.append(line)
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        
        return '\n'.join(cleaned_lines)
    
    def _analyze_response(self, response: str) -> Dict[str, Any]:
        """Analizar respuesta para métricas"""
        return {
            "length": len(response),
            "word_count": len(response.split()),
            "has_code": "```" in response,
            "has_explanations": any(word in response.lower() for word in ["explicación", "explanation", "porque", "because"]),
            "structure_score": self._calculate_structure_score(response)
        }
    
    def _calculate_structure_score(self, response: str) -> float:
        """Calcular puntuación de estructura"""
        score = 0.0
        
        # Puntos por tener código
        if "```" in response:
            score += 0.3
        
        # Puntos por tener explicaciones
        if any(word in response.lower() for word in ["explicación", "explanation"]):
            score += 0.2
        
        # Puntos por tener estructura clara
        if any(marker in response for marker in ["**", "##", "###"]):
            score += 0.2
        
        # Puntos por tener ejemplos
        if any(word in response.lower() for word in ["ejemplo", "example", "caso"]):
            score += 0.2
        
        # Puntos por tener conclusiones
        if any(word in response.lower() for word in ["conclusión", "conclusion", "resumen", "summary"]):
            score += 0.1
        
        return min(score, 1.0)
    
    def _identify_improvements(self, original: Dict[str, Any], optimized: Dict[str, Any]) -> List[str]:
        """Identificar mejoras realizadas"""
        improvements = []
        
        if optimized["structure_score"] > original["structure_score"]:
            improvements.append("Mejorada estructura y organización")
        
        if optimized["has_explanations"] and not original["has_explanations"]:
            improvements.append("Agregadas explicaciones detalladas")
        
        if optimized["has_code"] and not original["has_code"]:
            improvements.append("Agregado código de ejemplo")
        
        if optimized["word_count"] > original["word_count"] * 1.1:
            improvements.append("Expandido contenido para mayor detalle")
        elif optimized["word_count"] < original["word_count"] * 0.9:
            improvements.append("Optimizado para mayor concisión")
        
        return improvements
    
    def _calculate_quality_score(self, response: str) -> float:
        """Calcular puntuación de calidad"""
        score = 0.0
        
        # Puntuación base por estructura
        score += self._calculate_structure_score(response)
        
        # Puntuación por completitud
        if len(response) > 100:
            score += 0.2
        
        # Puntuación por claridad
        if not any(word in response.lower() for word in ["error", "undefined", "null"]):
            score += 0.1
        
        # Puntuación por utilidad
        if any(word in response.lower() for word in ["código", "code", "ejemplo", "example"]):
            score += 0.2
        
        return min(score, 1.0)
    
    def _estimate_cost(self, response: str) -> float:
        """Estimar costo de la respuesta"""
        # Estimación básica basada en tokens
        token_count = len(response.split())
        cost_per_token = 0.0001  # Estimación aproximada
        return token_count * cost_per_token
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento"""
        if not self.metrics_history:
            return {"message": "No hay métricas disponibles"}
        
        recent_metrics = self.metrics_history[-10:]  # Últimas 10 optimizaciones
        
        return {
            "total_optimizations": len(self.metrics_history),
            "average_response_time": sum(m.response_time for m in recent_metrics) / len(recent_metrics),
            "average_quality_score": sum(m.quality_score for m in recent_metrics) / len(recent_metrics),
            "average_token_count": sum(m.token_count for m in recent_metrics) / len(recent_metrics),
            "total_cost_estimate": sum(m.cost_estimate for m in recent_metrics)
        }
    
    def optimize_batch(self, prompts: List[str], contexts: List[Dict[str, Any]]) -> List[str]:
        """Optimizar múltiples prompts en lote"""
        try:
            optimized_prompts = []
            
            for prompt, context in zip(prompts, contexts):
                optimized = self._apply_prompt_optimization(prompt, context)
                optimized_prompts.append(optimized)
            
            self.logger.info(f"Optimizados {len(prompts)} prompts en lote")
            return optimized_prompts
            
        except Exception as e:
            self.logger.error(f"Error en optimización en lote: {e}")
            return prompts
