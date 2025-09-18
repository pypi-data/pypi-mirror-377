"""
Módulo de dinámica para análisis de fuerzas y movimiento.

Este paquete contiene herramientas para el análisis dinámico de sistemas físicos,
incluyendo las leyes de Newton, análisis de fuerzas, trabajo, energía, choques,
sistemas de partículas y dinámica rotacional.
"""

from .newton import LeyesNewton
from .fuerzas import AnalisisFuerzas
from .trabajo_energia import TrabajoEnergia
from .choques import ChoquesColisiones
from .sistemas_particulas import SistemasParticulas
from . import rotacional

__all__ = [
    "LeyesNewton",
    "AnalisisFuerzas",
    "TrabajoEnergia",
    "ChoquesColisiones",
    "SistemasParticulas",
    "rotacional"
]
