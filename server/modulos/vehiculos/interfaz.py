from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class iControlVehiculos(ABC):
    """
    CONTRATO DE SERVICIO (Interfaz ofrecida por Gestión de Vehículos)
    Define qué puede solicitar Gestión de Reservaciones sin conocer las tablas internas.
    """

    @abstractmethod
    def listar_vehiculos(self) -> List[Dict]:
        pass

    @abstractmethod
    def verificar_estado_y_disponibilidad(self, id_vehiculo: int) -> Optional[Dict]:
        """
        Entrada: id_vehiculo
        Resultado: Diccionario con estado actual y conteo de fallas críticas pendientes.
        """
        pass

    @abstractmethod
    def actualizar_estado_vehiculo(self, id_vehiculo: int, nuevo_estado: str) -> bool:
        """
        Entrada: id_vehiculo, nuevo_estado
        Condición: El vehículo debe existir.
        Resultado: True si se actualizó correctamente en Db2.
        """
        pass
