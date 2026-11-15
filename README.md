# UV Move — Prueba de Concepto (Actividad 10)

**Equipo #8:** Gael Pacheco de los Santos e Ian Jesús Sánchez Flores  
**Experiencia Educativa:** Diseño y Arquitectura de Software (19212) — Universidad Veracruzana  

---

## 1. Propósito y Alcance de la PoC
Esta Prueba de Concepto materializa y valida la colaboración entre dos módulos principales de la arquitectura de **UV Move**:
* **Módulo Solicitante:** `Gestión de Reservaciones` (`server/modulos/reservaciones/servicio.py`)
* **Módulo Proveedor:** `Gestión de Vehículos` (`server/modulos/vehiculos/servicio.py`)

Ambos módulos colaboran exclusivamente a través del contrato definido en la interfaz **`iControlVehiculos`** (`server/modulos/vehiculos/interfaz.py`), garantizando bajo acoplamiento y ocultamiento de detalles de persistencia.

---

## 2. Stack Tecnológico y Responsabilidades
| Capa / Responsabilidad | Tecnología | Uso en la PoC |
| :--- | :--- | :--- |
| **Frontend** | React + Vite (`client/`) | Interfaz web mínima alineada al prototipo navegable de Figma (Pantallas 01 y 03). |
| **Identidad / Autenticación** | Supabase Auth | Control de acceso institucional para validar usuarios universitarios activos (`RN1`). |
| **Lógica de Módulos** | Python + FastAPI (`server/`) | Separación lógica entre solicitante y proveedor, ejecución de contratos y reglas de negocio. |
| **Base de Datos de Negocio** | IBM Db2 (`UVMOVE`) | Fuente única de persistencia relacional para vehículos, fallas y reservaciones. |
| **Control de Versiones** | Git + GitHub | Historial de evolución del esquema SQL (`v1.0` → `v1.1`) y código fuente. |

---

## 3. Evolución y Versionado del Modelo de Datos
* **`database/DB_MODEL_v1.0.sql`:** Esquema base de la Entrega 8 compuesto por las entidades `VEHICULO`, `REPORTE_FALLA` y `REVISION_MANTENIMIENTO`.
* **`database/DB_MODEL_v1.1.sql`:** Evolución formal del esquema justificada por los requisitos **R6**, **R7** y las reglas **RN3**, **RN4** (requeridos para soportar el flujo de reservaciones diseñado en los mockups de Figma de la Entrega 9). Se incorporó la entidad **`RESERVACION`** vinculada mediante clave foránea a `VEHICULO`, junto con el cálculo automático de vigencia de 10 minutos (`CURRENT_TIMESTAMP + 10 MINUTES`).

---

## 4. Trazabilidad Final (Requisito → Diseño → Implementación)
| Elemento | Evidencia en la PoC |
| :--- | :--- |
| **Requisito** | **R6** (Reservar vehículo disponible), **R7** (Impedir asignación doble), **R17** (Bloqueo preventivo ante falla crítica). |
| **Regla de negocio** | **RN3** (Solo estado `DISPONIBLE`), **RN4** (Vigencia máxima de 10 minutos), **RN13** (Vehículo con falla crítica bloqueado hasta revisión `SEGURO`). |
| **Módulo solicitante** | `Gestión de Reservaciones` (`server/modulos/reservaciones/servicio.py`) |
| **Interfaz / servicio** | `iControlVehiculos` → `verificar_estado_y_disponibilidad(id_vehiculo)` y `actualizar_estado_vehiculo(id_vehiculo, nuevo_estado)` |
| **Contrato** | **Entrada:** `id_vehiculo`, `usuario_email`. **Condición:** Usuario autenticado en Supabase Auth y vehículo en estado `DISPONIBLE` sin reportes críticos pendientes. **Resultado:** Persistencia en `RESERVACION` con expiración a 10 min y actualización del vehículo a `RESERVADO`. |
| **Módulo proveedor** | `Gestión de Vehículos` (`server/modulos/vehiculos/servicio.py`) |
| **Entidades Db2 involucradas** | `VEHICULO`, `REPORTE_FALLA` (`v1.0`) y `RESERVACION` (`v1.1`) |
| **Escenario 1 (Exitoso)** | Usuario autenticado selecciona `UV-042` (`DISPONIBLE`) → `GestionVehiculosService` confirma estado → `GestionReservacionesService` registra la reserva en Db2 y actualiza `UV-042` a `RESERVADO`. |
| **Escenario 2 (Rechazo por RN)** | Usuario intenta reservar `UV-031` (`BLOQUEADO`) → `GestionVehiculosService` reporta falla crítica pendiente → `GestionReservacionesService` aplica **RN13**, impide la inserción en Db2 y muestra el motivo de rechazo en pantalla. |

---

## 5. Instrucciones de Ejecución Local
1. **Base de datos IBM Db2 (Docker):**
   ```bash
   docker start db2-uvmove
# uv-move-poc
