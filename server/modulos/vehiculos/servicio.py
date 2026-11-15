import ibm_db
from typing import List, Dict, Optional
from db2_conn import get_connection
from modulos.vehiculos.interfaz import iControlVehiculos

class GestionVehiculosService(iControlVehiculos):
    """Implementación del Módulo Proveedor: Gestión de Vehículos"""

    def listar_vehiculos(self) -> List[Dict]:
        conn = get_connection()
        try:
            sql = """
                SELECT v.id_vehiculo, v.placa, v.tipo, v.estado,
                       (SELECT COUNT(*) FROM REPORTE_FALLA rf 
                        WHERE rf.id_vehiculo = v.id_vehiculo 
                          AND rf.criticidad = 'CRITICA' 
                          AND rf.estado <> 'CERRADO') AS fallas_criticas
                FROM VEHICULO v
                ORDER BY v.id_vehiculo
            """
            stmt = ibm_db.exec_immediate(conn, sql)
            vehiculos = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                vehiculos.append({
                    "id_vehiculo": row["ID_VEHICULO"],
                    "placa": row["PLACA"],
                    "tipo": row["TIPO"],
                    "estado": row["ESTADO"],
                    "fallas_criticas": row["FALLAS_CRITICAS"]
                })
                row = ibm_db.fetch_assoc(stmt)
            return vehiculos
        finally:
            ibm_db.close(conn)

    def verificar_estado_y_disponibilidad(self, id_vehiculo: int) -> Optional[Dict]:
        conn = get_connection()
        try:
            sql = """
                SELECT v.id_vehiculo, v.placa, v.tipo, v.estado,
                       (SELECT COUNT(*) FROM REPORTE_FALLA rf 
                        WHERE rf.id_vehiculo = v.id_vehiculo 
                          AND rf.criticidad = 'CRITICA' 
                          AND rf.estado <> 'CERRADO') AS fallas_criticas
                FROM VEHICULO v
                WHERE v.id_vehiculo = ?
            """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, id_vehiculo)
            ibm_db.execute(stmt)
            row = ibm_db.fetch_assoc(stmt)
            if not row:
                return None
            return {
                "id_vehiculo": row["ID_VEHICULO"],
                "placa": row["PLACA"],
                "tipo": row["TIPO"],
                "estado": row["ESTADO"],
                "fallas_criticas": row["FALLAS_CRITICAS"]
            }
        finally:
            ibm_db.close(conn)

    def actualizar_estado_vehiculo(self, id_vehiculo: int, nuevo_estado: str) -> bool:
        conn = get_connection()
        try:
            sql = "UPDATE VEHICULO SET estado = ?, fecha_actualizacion = CURRENT_TIMESTAMP WHERE id_vehiculo = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, nuevo_estado)
            ibm_db.bind_param(stmt, 2, id_vehiculo)
            return ibm_db.execute(stmt)
        finally:
            ibm_db.close(conn)
