from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from modulos.vehiculos.servicio import GestionVehiculosService
from modulos.reservaciones.servicio import GestionReservacionesService, ReglaNegocioException

app = FastAPI(title="UV Move PoC - Arquitectura de Componentes")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inyección de dependencias respetando el contrato iControlVehiculos
vehiculos_service = GestionVehiculosService()
reservaciones_service = GestionReservacionesService(vehiculos_provider=vehiculos_service)

class SolicitudReserva(BaseModel):
    id_vehiculo: int
    usuario_email: str

@app.get("/api/vehiculos")
def obtener_vehiculos():
    return vehiculos_service.listar_vehiculos()

@app.get("/api/reservaciones")
def obtener_reservaciones():
    return reservaciones_service.listar_reservaciones()

@app.post("/api/reservaciones")
def crear_reservacion(payload: SolicitudReserva):
    try:
        return reservaciones_service.crear_reservacion(
            id_vehiculo=payload.id_vehiculo,
            usuario_email=payload.usuario_email
        )
    except ReglaNegocioException as e:
        raise HTTPException(
            status_code=400,
            detail={"regla": e.regla, "mensaje": e.mensaje}
        )
