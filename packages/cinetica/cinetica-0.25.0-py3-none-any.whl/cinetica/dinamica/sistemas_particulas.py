"""
Módulo de Sistemas de Partículas para análisis dinámico.

Este módulo proporciona herramientas para analizar sistemas de partículas,
incluyendo cálculo de centro de masa, momento de inercia, teorema de los ejes
paralelos (Steiner) y energía cinética rotacional.
"""

from typing import List, Union, Tuple, Optional
import numpy as np
from ..units import ureg, Q_


class SistemasParticulas:
    """
    Clase para el análisis de sistemas de partículas en dinámica.
    
    Esta clase proporciona métodos para calcular propiedades de sistemas de
    partículas, incluyendo centro de masa, momento de inercia, teorema de
    Steiner y energía cinética rotacional.
    
    Examples
    --------
    >>> from cinetica.dinamica import SistemasParticulas
    >>> sp = SistemasParticulas()
    >>> # Calcular centro de masa
    >>> masas = [1.0, 2.0, 3.0]  # kg
    >>> posiciones = [[0,0,0], [1,1,0], [2,0,0]]  # m
    >>> cm = sp.centro_masa(masas, posiciones)
    """
    
    def __init__(self):
        """Inicializa la clase SistemasParticulas."""
        pass
    
    def centro_masa(
        self,
        masas: List[float],
        posiciones: List[List[float]],
        unidades: Optional[dict] = None
    ) -> np.ndarray:
        """
        Calcula el centro de masa de un sistema de partículas.
        
        Parameters
        ----------
        masas : List[float]
            Lista de masas de las partículas.
        posiciones : List[List[float]]
            Lista de posiciones [x, y, z] de cada partícula.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            Ejemplo: {'masa': 'kg', 'longitud': 'm'}
            
        Returns
        -------
        np.ndarray
            Vector de posición del centro de masa [x_cm, y_cm, z_cm].
            
        Raises
        ------
        ValueError
            Si las longitudes de las listas de masas y posiciones no coinciden.
        """
        if len(masas) != len(posiciones):
            raise ValueError("Las listas de masas y posiciones deben tener la misma longitud.")
        
        # Aplicar unidades si se especifican o si ya son cantidades con unidades
        has_units = (unidades is not None) or (hasattr(masas, 'units') and hasattr(posiciones[0], 'units'))
        
        if has_units:
            if not hasattr(masas, 'units'):
                masas = Q_(masas, unidades.get('masa', ''))
            if not hasattr(posiciones[0], 'units'):
                posiciones = [Q_(p, unidades.get('longitud', '')) for p in posiciones]
        else:
            # Convertir a arrays de numpy si no hay unidades
            masas = np.asarray(masas, dtype=float)
            posiciones = np.asarray(posiciones, dtype=float)
        
        # Calcular centro de masa: sum(m_i * r_i) / sum(m_i)
        if has_units:
            masa_total = sum(masas)
            if masa_total == 0:
                raise ValueError("La suma de las masas no puede ser cero.")
                
            # Calcular el numerador: sum(m_i * r_i)
            numerador = sum(m * p for m, p in zip(masas, posiciones))
            cm = numerador / masa_total
            
            # Convertir a array de numpy con magnitudes
            cm = np.array([v.magnitude for v in cm])
        else:
            # Versión sin unidades
            masa_total = np.sum(masas)
            if masa_total == 0:
                raise ValueError("La suma de las masas no puede ser cero.")
                
            cm = np.sum(masas[:, np.newaxis] * posiciones, axis=0) / masa_total
        
        return cm
    
    def momento_inercia_particula(
        self,
        masa: float,
        posicion: List[float],
        eje: Optional[List[float]] = None,
        unidades: Optional[dict] = None
    ) -> float:
        """
        Calcula el momento de inercia de una partícula con respecto a un eje.
        
        Parameters
        ----------
        masa : float
            Masa de la partícula.
        posicion : List[float]
            Vector de posición [x, y, z] de la partícula.
        eje : List[float], opcional
            Vector unitario que define la dirección del eje.
            Si es None, se calcula con respecto al origen.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            
        Returns
        -------
        float
            Momento de inercia de la partícula con respecto al eje.
        """
        # Aplicar unidades si se especifican
        if unidades:
            masa = Q_(masa, unidades.get('masa', ''))
            posicion = Q_(posicion, unidades.get('longitud', ''))
        else:
            # Convertir a arrays de numpy si no hay unidades
            posicion = np.asarray(posicion, dtype=float)
        
        if eje is None:
            # Momento de inercia con respecto al origen
            r_cuad = np.sum(posicion**2)
            I = masa * r_cuad
        else:
            # Momento de inercia con respecto a un eje arbitrario
            eje = np.asarray(eje, dtype=float)
            eje = eje / np.linalg.norm(eje)  # Normalizar vector
            
            # Distancia perpendicular al eje: |r × e|
            r_cruz_e = np.cross(posicion, eje)
            d_perp_cuad = np.sum(r_cruz_e**2)
            I = masa * d_perp_cuad
        
        # Extraer el valor numérico si es una cantidad con unidades
        if hasattr(I, 'magnitude'):
            I = I.magnitude
            
        return I
    
    def momento_inercia_sistema(
        self,
        masas: List[float],
        posiciones: List[List[float]],
        eje: Optional[List[float]] = None,
        unidades: Optional[dict] = None
    ) -> float:
        """
        Calcula el momento de inercia de un sistema de partículas con respecto a un eje.
        
        Parameters
        ----------
        masas : List[float]
            Lista de masas de las partículas.
        posiciones : List[List[float]]
            Lista de posiciones [x, y, z] de cada partícula.
        eje : List[float], opcional
            Vector unitario que define la dirección del eje.
            Si es None, se calcula con respecto al origen.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            
        Returns
        -------
        float
            Momento de inercia total del sistema con respecto al eje.
        """
        if len(masas) != len(posiciones):
            raise ValueError("Las listas de masas y posiciones deben tener la misma longitud.")
        
        I_total = 0.0
        
        for masa, posicion in zip(masas, posiciones):
            I_total += self.momento_inercia_particula(masa, posicion, eje, unidades)
        
        return I_total
    
    def teorema_steiner(
        self,
        I_cm: float,
        masa_total: float,
        distancia: float,
        unidades: Optional[dict] = None
    ) -> float:
        """
        Aplica el teorema de los ejes paralelos (Steiner) para calcular el momento de inercia.
        
        I = I_cm + M * d²
        
        Donde:
        - I: Momento de inercia con respecto al nuevo eje
        - I_cm: Momento de inercia con respecto al centro de masa
        - M: Masa total del sistema
        - d: Distancia entre los ejes paralelos
        
        Parameters
        ----------
        I_cm : float
            Momento de inercia con respecto al centro de masa.
        masa_total : float
            Masa total del sistema.
        distancia : float
            Distancia entre los ejes paralelos.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            
        Returns
        -------
        float
            Momento de inercia con respecto al nuevo eje.
        """
        # Aplicar unidades si se especifican
        if unidades:
            I_cm = Q_(I_cm, unidades.get('momento_inercia', ''))
            masa_total = Q_(masa_total, unidades.get('masa', ''))
            distancia = Q_(distancia, unidades.get('longitud', ''))
        
        # Aplicar el teorema de Steiner
        I = I_cm + masa_total * distancia**2
        
        # Extraer el valor numérico si es una cantidad con unidades
        if hasattr(I, 'magnitude'):
            I = I.magnitude
            
        return I
    
    def energia_cinetica_rotacional(
        self,
        momento_inercia: float,
        velocidad_angular: float,
        unidades: Optional[dict] = None
    ) -> float:
        """
        Calcula la energía cinética rotacional de un cuerpo rígido.
        
        K = (1/2) * I * ω²
        
        Donde:
        - K: Energía cinética rotacional
        - I: Momento de inercia
        - ω: Velocidad angular
        
        Parameters
        ----------
        momento_inercia : float
            Momento de inercia del cuerpo.
        velocidad_angular : float
            Velocidad angular del cuerpo.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            
        Returns
        -------
        float
            Energía cinética rotacional.
        """
        # Aplicar unidades si se especifican
        if unidades:
            momento_inercia = Q_(momento_inercia, unidades.get('momento_inercia', ''))
            velocidad_angular = Q_(velocidad_angular, unidades.get('velocidad_angular', ''))
        
        # Calcular energía cinética rotacional
        K = 0.5 * momento_inercia * velocidad_angular**2
        
        # Extraer el valor numérico si es una cantidad con unidades
        if hasattr(K, 'magnitude'):
            K = K.magnitude
            
        return K
    
    def momento_angular(
        self,
        momento_inercia: float,
        velocidad_angular: float,
        unidades: Optional[dict] = None
    ) -> float:
        """
        Calcula el momento angular de un cuerpo rígido.
        
        L = I * ω
        
        Donde:
        - L: Momento angular
        - I: Momento de inercia
        - ω: Velocidad angular
        
        Parameters
        ----------
        momento_inercia : float
            Momento de inercia del cuerpo.
        velocidad_angular : float
            Velocidad angular del cuerpo.
        unidades : dict, opcional
            Diccionario con las unidades de las magnitudes de entrada.
            
        Returns
        -------
        float
            Momento angular.
        """
        # Aplicar unidades si se especifican
        if unidades:
            momento_inercia = Q_(momento_inercia, unidades.get('momento_inercia', ''))
            velocidad_angular = Q_(velocidad_angular, unidades.get('velocidad_angular', ''))
        
        # Calcular momento angular
        L = momento_inercia * velocidad_angular
        
        # Extraer el valor numérico si es una cantidad con unidades
        if hasattr(L, 'magnitude'):
            L = L.magnitude
            
        return L
