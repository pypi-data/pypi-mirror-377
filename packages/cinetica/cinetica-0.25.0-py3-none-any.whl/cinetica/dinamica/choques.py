"""
Módulo de Choques y Colisiones para análisis dinámico.

Este módulo implementa las leyes de conservación del momento lineal y energía
para el análisis de colisiones elásticas e inelásticas en 1D, 2D y 3D.
"""

from typing import Union, Tuple, List, Optional
import numpy as np
from ..units import ureg, Q_


class ChoquesColisiones:
    """
    Clase para el análisis de choques y colisiones en sistemas físicos.
    
    Esta clase proporciona métodos para analizar colisiones elásticas e inelásticas,
    calcular velocidades finales, momento lineal y coeficientes de restitución.
    
    Examples
    --------
    >>> from cinetica.dinamica import ChoquesColisiones
    >>> choques = ChoquesColisiones()
    >>> # Colisión elástica en 1D
    >>> v1f, v2f = choques.colision_unidimensional(
    ...     m1=2, v1i=3, m2=5, v2i=-1, coeficiente_restitucion=1.0
    ... )
    """
    
    def __init__(self):
        """Inicializa la clase ChoquesColisiones."""
        pass
    
    def colision_unidimensional(
        self,
        m1: float,
        v1i: float,
        m2: float,
        v2i: float,
        coeficiente_restitucion: float = 1.0,
        unidades: Optional[dict] = None
    ) -> Tuple[float, float]:
        """
        Analiza una colisión unidimensional entre dos partículas.
        
        Parameters
        ----------
        m1 : float
            Masa de la primera partícula.
        v1i : float
            Velocidad inicial de la primera partícula.
        m2 : float
            Masa de la segunda partícula.
        v2i : float
            Velocidad inicial de la segunda partícula.
        coeficiente_restitucion : float, opcional
            Coeficiente de restitución (0 para colisión perfectamente inelástica,
            1 para colisión perfectamente elástica). Por defecto 1.0.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            Ejemplo: {'masa': 'kg', 'velocidad': 'm/s'}
            
        Returns
        -------
        tuple
            Tupla con las velocidades finales (v1f, v2f).
            
        Raises
        ------
        ValueError
            Si el coeficiente de restitución no está en el rango [0, 1].
        """
        if not 0 <= coeficiente_restitucion <= 1:
            raise ValueError("El coeficiente de restitución debe estar entre 0 y 1.")
            
        # Aplicar unidades si se especifican
        if unidades:
            m1 = Q_(m1, unidades.get('masa', ''))
            v1i = Q_(v1i, unidades.get('velocidad', ''))
            m2 = Q_(m2, unidades.get('masa', ''))
            v2i = Q_(v2i, unidades.get('velocidad', ''))
        
        # Conservación del momento lineal
        # m1*v1i + m2*v2i = m1*v1f + m2*v2f
        
        # Coeficiente de restitución
        # e = -(v2f - v1f)/(v2i - v1i)
        
        # Resolver el sistema de ecuaciones
        v1f = (m1 - m2 * coeficiente_restitucion) * v1i + \
              m2 * (1 + coeficiente_restitucion) * v2i
        v1f /= (m1 + m2)
        
        v2f = m1 * (1 + coeficiente_restitucion) * v1i + \
              (m2 - m1 * coeficiente_restitucion) * v2i
        v2f /= (m1 + m2)
        
        # Extraer el valor numérico si son cantidades con unidades
        if hasattr(v1f, 'magnitude'):
            v1f = v1f.magnitude
            v2f = v2f.magnitude
        
        return v1f, v2f
    
    def colision_bidimensional(
        self,
        m1: float,
        v1i: Union[float, List[float], np.ndarray],
        m2: float,
        v2i: Union[float, List[float], np.ndarray],
        angulo_impacto: float,
        coeficiente_restitucion: float = 1.0,
        unidades: Optional[dict] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Analiza una colisión bidimensional entre dos partículas.
        
        Parameters
        ----------
        m1 : float
            Masa de la primera partícula.
        v1i : array_like
            Vector velocidad inicial de la primera partícula [vx, vy].
        m2 : float
            Masa de la segunda partícula.
        v2i : array_like
            Vector velocidad inicial de la segunda partícula [vx, vy].
        angulo_impacto : float
            Ángulo de impacto en radianes.
        coeficiente_restitucion : float, opcional
            Coeficiente de restitución (0-1). Por defecto 1.0.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            
        Returns
        -------
        tuple
            Tupla con los vectores velocidad final (v1f, v2f).
        """
        if not 0 <= coeficiente_restitucion <= 1:
            raise ValueError("El coeficiente de restitución debe estar entre 0 y 1.")
            
        # Convertir a arrays de numpy si es necesario
        v1i = np.asarray(v1i, dtype=float)
        v2i = np.asarray(v2i, dtype=float)
        
        # Aplicar unidades si se especifican
        if unidades:
            m1 = Q_(m1, unidades.get('masa', ''))
            m2 = Q_(m2, unidades.get('masa', ''))
            v1i = Q_(v1i, unidades.get('velocidad', ''))
            v2i = Q_(v2i, unidades.get('velocidad', ''))
        
        # Matriz de rotación para el sistema de coordenadas de la colisión
        c, s = np.cos(angulo_impacto), np.sin(angulo_impacto)
        R = np.array([[c, -s], [s, c]])
        
        # Rotar velocidades al sistema de coordenadas de la colisión
        v1i_rot = R @ v1i
        v2i_rot = R @ v2i
        
        # Velocidad relativa en la dirección normal
        v_rel_normal = v1i_rot[0] - v2i_rot[0]
        
        # Calcular velocidades finales en la dirección normal
        v1f_rot = np.zeros_like(v1i_rot)
        v2f_rot = np.zeros_like(v2i_rot)
        
        # Conservación del momento lineal en la dirección normal
        v1f_rot[0] = ((m1 - coeficiente_restitucion * m2) * v1i_rot[0] +
                      (1 + coeficiente_restitucion) * m2 * v2i_rot[0]) / (m1 + m2)
        v2f_rot[0] = ((1 + coeficiente_restitucion) * m1 * v1i_rot[0] +
                      (m2 - coeficiente_restitucion * m1) * v2i_rot[0]) / (m1 + m2)
        
        # Las velocidades tangenciales no cambian
        v1f_rot[1] = v1i_rot[1]
        v2f_rot[1] = v2i_rot[1]
        
        # Rotar de vuelta al sistema de coordenadas original
        R_inv = R.T  # La inversa de una matriz de rotación es su transpuesta
        v1f = R_inv @ v1f_rot
        v2f = R_inv @ v2f_rot
        
        # Extraer el valor numérico si son cantidades con unidades
        if hasattr(v1f[0], 'magnitude'):
            v1f = np.array([v.magnitude for v in v1f])
            v2f = np.array([v.magnitude for v in v2f])
        
        return v1f, v2f
    
    def colision_tridimensional(
        self,
        m1: float,
        v1i: Union[List[float], np.ndarray],
        m2: float,
        v2i: Union[List[float], np.ndarray],
        normal_impacto: Union[List[float], np.ndarray],
        coeficiente_restitucion: float = 1.0,
        unidades: Optional[dict] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Analiza una colisión tridimensional entre dos partículas.
        
        Parameters
        ----------
        m1 : float
            Masa de la primera partícula.
        v1i : array_like
            Vector velocidad inicial de la primera partícula [vx, vy, vz].
        m2 : float
            Masa de la segunda partícula.
        v2i : array_like
            Vector velocidad inicial de la segunda partícula [vx, vy, vz].
        normal_impacto : array_like
            Vector normal al plano de impacto [nx, ny, nz].
        coeficiente_restitucion : float, opcional
            Coeficiente de restitución (0-1). Por defecto 1.0.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            
        Returns
        -------
        tuple
            Tupla con los vectores velocidad final (v1f, v2f).
        """
        if not 0 <= coeficiente_restitucion <= 1:
            raise ValueError("El coeficiente de restitución debe estar entre 0 y 1.")
            
        # Convertir a arrays de numpy
        v1i = np.asarray(v1i, dtype=float)
        v2i = np.asarray(v2i, dtype=float)
        normal = np.asarray(normal_impacto, dtype=float)
        
        # Normalizar el vector normal
        normal = normal / np.linalg.norm(normal)
        
        # Aplicar unidades si se especifican
        if unidades:
            m1 = Q_(m1, unidades.get('masa', ''))
            m2 = Q_(m2, unidades.get('masa', ''))
            v1i = Q_(v1i, unidades.get('velocidad', ''))
            v2i = Q_(v2i, unidades.get('velocidad', ''))
        
        # Calcular las componentes normal y tangencial
        v1i_normal = np.dot(v1i, normal) * normal
        v1i_tang = v1i - v1i_normal
        
        v2i_normal = np.dot(v2i, normal) * normal
        v2i_tang = v2i - v2i_normal
        
        # Calcular velocidades finales en la dirección normal
        v1f_normal = ((m1 - coeficiente_restitucion * m2) * v1i_normal +
                      (1 + coeficiente_restitucion) * m2 * v2i_normal) / (m1 + m2)
        v2f_normal = ((1 + coeficiente_restitucion) * m1 * v1i_normal +
                      (m2 - coeficiente_restitucion * m1) * v2i_normal) / (m1 + m2)
        
        # Las componentes tangenciales no cambian
        v1f = v1i_tang + v1f_normal
        v2f = v2i_tang + v2f_normal
        
        # Extraer el valor numérico si son cantidades con unidades
        if hasattr(v1f[0], 'magnitude'):
            v1f = np.array([v.magnitude for v in v1f])
            v2f = np.array([v.magnitude for v in v2f])
        
        return v1f, v2f
    
    def coeficiente_restitucion(
        self,
        v1i: float,
        v2i: float,
        v1f: float,
        v2f: float,
        unidades: Optional[dict] = None
    ) -> float:
        """
        Calcula el coeficiente de restitución a partir de las velocidades.
        
        Parameters
        ----------
        v1i : float
            Velocidad inicial del primer objeto.
        v2i : float
            Velocidad inicial del segundo objeto.
        v1f : float
            Velocidad final del primer objeto.
        v2f : float
            Velocidad final del segundo objeto.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            
        Returns
        -------
        float
            Coeficiente de restitución.
        """
        # Aplicar unidades si se especifican
        if unidades:
            v1i = Q_(v1i, unidades.get('velocidad', ''))
            v2i = Q_(v2i, unidades.get('velocidad', ''))
            v1f = Q_(v1f, unidades.get('velocidad', ''))
            v2f = Q_(v2f, unidades.get('velocidad', ''))
        
        # Calcular el coeficiente de restitución
        e = -(v2f - v1f) / (v2i - v1i)
        
        # Asegurar que el resultado esté en el rango [0, 1]
        e = max(0.0, min(float(e), 1.0))
        
        return e
    
    def energia_cinetica_perdida(
        self,
        m1: float,
        v1i: float,
        m2: float,
        v2i: float,
        v1f: Optional[float] = None,
        v2f: Optional[float] = None,
        coeficiente_restitucion: Optional[float] = None,
        unidades: Optional[dict] = None
    ) -> float:
        """
        Calcula la energía cinética perdida en una colisión.
        
        Parameters
        ----------
        m1 : float
            Masa del primer objeto.
        v1i : float
            Velocidad inicial del primer objeto.
        m2 : float
            Masa del segundo objeto.
        v2i : float
            Velocidad inicial del segundo objeto.
        v1f : float, opcional
            Velocidad final del primer objeto. Si no se proporciona, se calcula.
        v2f : float, opcional
            Velocidad final del segundo objeto. Si no se proporciona, se calcula.
        coeficiente_restitucion : float, opcional
            Coeficiente de restitución. Requerido si no se proporcionan v1f y v2f.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            
        Returns
        -------
        float
            Energía cinética perdida en la colisión.
            
        Raises
        ------
        ValueError
            Si no se proporcionan ni las velocidades finales ni el coeficiente de restitución.
        """
        # Aplicar unidades si se especifican
        if unidades:
            m1 = Q_(m1, unidades.get('masa', ''))
            m2 = Q_(m2, unidades.get('masa', ''))
            v1i = Q_(v1i, unidades.get('velocidad', ''))
            v2i = Q_(v2i, unidades.get('velocidad', ''))
            if v1f is not None:
                v1f = Q_(v1f, unidades.get('velocidad', ''))
            if v2f is not None:
                v2f = Q_(v2f, unidades.get('velocidad', ''))
        
        # Calcular velocidades finales si no se proporcionan
        if v1f is None or v2f is None:
            if coeficiente_restitucion is None:
                raise ValueError(
                    "Se requieren las velocidades finales o el coeficiente de restitución."
                )
            v1f, v2f = self.colision_unidimensional(
                m1, v1i, m2, v2i, coeficiente_restitucion
            )
        
        # Calcular energías cinéticas inicial y final
        K_i = 0.5 * m1 * v1i**2 + 0.5 * m2 * v2i**2
        K_f = 0.5 * m1 * v1f**2 + 0.5 * m2 * v2f**2
        
        # Calcular energía perdida
        delta_K = K_i - K_f
        
        # Asegurar que no sea negativa (por posibles errores de redondeo)
        delta_K = max(0.0, delta_K)
        
        # Extraer el valor numérico si es una cantidad con unidades
        if hasattr(delta_K, 'magnitude'):
            delta_K = delta_K.magnitude
        
        return delta_K
