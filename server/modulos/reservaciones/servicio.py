import ibm_db
from typing import Dict, List
from db2_conn import get_connection
from modulos.vehiculos.interfaz import iControlVehiculos

class ReglaNegocioException(Exception):
    def __init__(self, regla: str, mensaje: str):
        self.regla = regla
        self.mensaje = mensaje
        super().__init__(mensaje)

class GestionReservacionesService:
    """
    Módulo Solicitante: Gestión de Reservaciones
    Colabora con Gestión de Vehículos ÚNICAMENTE mediante el contrato iControlVehiculos.
    """

    def __init__(self, vehiculos_provider: iControlVehiculos):
        self.vehiculos = vehiculos_provider

    def crear_reservacion(self, id_vehiculo: int, usuario_email: str) -> Dict:
        # 1. Solicitar información al proveedor mediante el contrato
        vehiculo = self.vehiculos.verificar_estado_y_disponibilidad(id_vehiculo)
        if not vehiculo:
            raise ReglaNegocioException("VALIDACION", "El vehículo solicitado no existe.")

        # 2. Aplicar RN13: Bloqueo por falla crítica pendiente (R17 / RN13)
        if vehiculo["estado"] in ("BLOQUEADO", "MANTENIMIENTO") or vehiculo["fallas_criticas"] > 0:
            raise ReglaNegocioException(
                "RN13",
                f"Operación rechazada por RN13: El vehículo {vehiculo['placa']} presenta una falla crítica pendiente y está bloqueado hasta ser declarado SEGURO por mantenimiento."
            )

        # 3. Aplicar RN3: Solo puede reservarse si está DISPONIBLE
        if vehiculo["estado"] != "DISPONIBLE":
            raise ReglaNegocioException(
                "RN3",
                f"Operación rechazada por RN3: El vehículo {vehiculo['placa']} no está disponible (Estado actual: {vehiculo['estado']})."
            )

        # 4. Persistir reservación en Db2 aplicando RN4 (vigencia de 10 minutos)
        conn = get_connection()
        try:
            sql = """
                INSERT INTO RESERVACION (id_vehiculo, usuario_email, fecha_creacion, fecha_expiracion, estado)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + 10 MINUTES, 'ACTIVA')
            """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, id_vehiculo)
            ibm_db.bind_param(stmt, 2, usuario_email)
            ibm_db.execute(stmt)
        finally:
            ibm_db.close(conn)

        # 5. Solicitar al proveedor actualizar el estado del vehículo a RESERVADO
        self.vehiculos.actualizar_estado_vehiculo(id_vehiculo, "RESERVADO")

        return {
            "mensaje": f"Reservación confirmada para el vehículo {vehiculo['placa']}. Tienes 10 minutos para iniciar tu viaje (RN4).",
            "placa": vehiculo["placa"],
            "nuevo_estado": "RESERVADO"
        }

    def listar_reservaciones(self) -> List[Dict]:
        conn = get_connection()
        try:
            sql = """
                SELECT r.id_reservacion, v.placa, r.usuario_email,
                       VARCHAR_FORMAT(r.fecha_creacion, 'YYYY-MM-DD HH24:MI:SS') AS inicio,
                       VARCHAR_FORMAT(r.fecha_expiracion, 'YYYY-MM-DD HH24:MI:SS') AS expira,
                       r.estado
                FROM RESERVACION r
                JOIN VEHICULO v ON r.id_vehiculo = v.id_vehiculo
                ORDER BY r.id_reservacion DESC
            """
            stmt = ibm_db.exec_immediate(conn, sql)
            reservas = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                reservas.append({
                    "id_reservacion": row["ID_RESERVACION"],
                    "placa": row["PLACA"],
                    "usuario_email": row["USUARIO_EMAIL"],
                    "inicio": row["INICIO"],
                    "expira": row["EXPIRA"],
                    "estado": row["ESTADO"]
                })
                row = ibm_db.fetch_assoc(stmt)
            return reservas
        finally:
            ibm_db.close(conn)
