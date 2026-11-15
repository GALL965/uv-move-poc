-- Evolución DB_MODEL_v1.1
-- Justificación: En la entrega 8 (v1.0) solo se modelaron VEHICULO, REPORTE_FALLA y REVISION_MANTENIMIENTO.
-- Para soportar el flujo de reservaciones diseñado en Figma (Act. 9) y cumplir R6, R7, RN3 y RN4,
-- se incorpora la entidad RESERVACION y se cargan datos iniciales para pruebas.

CREATE TABLE RESERVACION (
    id_reservacion INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_vehiculo INT NOT NULL,
    usuario_email VARCHAR(150) NOT NULL,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('ACTIVA', 'EXPIRADA', 'CANCELADA', 'COMPLETADA')),
    CONSTRAINT fk_reserva_vehiculo FOREIGN KEY (id_vehiculo) REFERENCES VEHICULO(id_vehiculo)
);

-- Datos semilla (Coinciden con los vehículos mostrados en Figma Act. 9)
INSERT INTO VEHICULO (placa, tipo, estado) VALUES ('UV-042', 'Bicicleta urbana', 'DISPONIBLE');
INSERT INTO VEHICULO (placa, tipo, estado) VALUES ('UV-018', 'Scooter eléctrico', 'DISPONIBLE');
INSERT INTO VEHICULO (placa, tipo, estado) VALUES ('UV-031', 'Bicicleta urbana', 'BLOQUEADO');

INSERT INTO REPORTE_FALLA (id_vehiculo, reportado_por, tipo_falla, criticidad, descripcion, estado)
VALUES (3, 'laura.mendez@estudiantes.uv.mx', 'Frenos', 'CRITICA', 'Freno delantero sin respuesta', 'PENDIENTE');
