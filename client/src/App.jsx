import { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import './App.css';

const API_URL = 'http://127.0.0.1:8000/api';

export default function App() {
  const [session, setSession] = useState(null);
  const [email, setEmail] = useState('laura.mendez@estudiantes.uv.mx');
  const [password, setPassword] = useState('uvmove123');
  const [authMsg, setAuthMsg] = useState('');

  const [vehiculos, setVehiculos] = useState([]);
  const [reservaciones, setReservaciones] = useState([]);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => setSession(session));
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });
    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (session) {
      cargarDatos();
    }
  }, [session]);

  const cargarDatos = async () => {
    try {
      const [resV, resR] = await Promise.all([
        fetch(`${API_URL}/vehiculos`),
        fetch(`${API_URL}/reservaciones`)
      ]);
      setVehiculos(await resV.json());
      setReservaciones(await resR.json());
    } catch (err) {
      setFeedback({ tipo: 'error', texto: 'No se pudo conectar con el servidor FastAPI / IBM Db2.' });
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthMsg('');
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) setAuthMsg(`Error de autenticación: ${error.message}`);
  };

  const handleSignUp = async () => {
    setAuthMsg('');
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) setAuthMsg(`Error al registrar: ${error.message}`);
    else setAuthMsg('Usuario registrado en Supabase Auth. Ahora haz clic en "Entrar al portal".');
  };

  const handleReservar = async (idVehiculo) => {
    setFeedback(null);
    try {
      const response = await fetch(`${API_URL}/reservaciones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_vehiculo: idVehiculo,
          usuario_email: session.user.email
        })
      });
      const data = await response.json();

      if (!response.ok) {
        setFeedback({
          tipo: 'error',
          texto: `[${data.detail.regla}] ${data.detail.mensaje}`
        });
      } else {
        setFeedback({
          tipo: 'success',
          texto: data.mensaje
        });
        cargarDatos();
      }
    } catch (err) {
      setFeedback({ tipo: 'error', texto: 'Error de comunicación con el backend.' });
    }
  };

  if (!session) {
    return (
      <div className="login-wrapper">
        <div className="login-banner">
          <div style={{ fontWeight: 800, fontSize: '1.3rem' }}>uvmove</div>
          <div>
            <h1>Tu campus,<br />en movimiento.</h1>
            <p>Una forma más simple, segura y sostenible de recorrer la Universidad Veracruzana.</p>
          </div>
          <small>Autenticación institucional vía Supabase Auth</small>
        </div>

        <div className="login-form-box">
          <form className="login-card" onSubmit={handleLogin}>
            <h2>Bienvenido de vuelta</h2>
            <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>Ingresa con tu cuenta institucional para continuar.</p>

            <label>Correo institucional</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />

            <label>Contraseña</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />

            {authMsg && <p style={{ color: '#b91c1c', fontSize: '0.85rem', marginTop: '0.75rem' }}>{authMsg}</p>}

            <button type="submit" className="btn-primary">Entrar al portal →</button>
            <button type="button" className="btn-secondary" onClick={handleSignUp}>
              Registrar usuario de prueba en Supabase
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div>
          <div className="brand">uvmove</div>
          <div className="nav-item">🚲 Reservar vehículo</div>
        </div>
        <div>
          <p style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.2rem' }}>{session.user.email}</p>
          <small style={{ color: '#16794c' }}>● Estudiante activo (Supabase)</small>
          <button className="btn-secondary" onClick={() => supabase.auth.signOut()}>Cerrar sesión</button>
        </div>
      </aside>

      <main className="main-content">
        <h2 style={{ marginTop: 0 }}>Reservar vehículo</h2>
        <p style={{ color: '#6b7280' }}>
          Selecciona una unidad. Tu reservación tendrá una vigencia máxima de <strong>10 minutos (RN4)</strong>.
        </p>

        {feedback && (
          <div className={`alert ${feedback.tipo === 'success' ? 'alert-success' : 'alert-error'}`}>
            {feedback.texto}
          </div>
        )}

        <div className="vehiculo-grid">
          {vehiculos.map((v) => (
            <div key={v.id_vehiculo} className="vehiculo-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong style={{ fontSize: '1.15rem' }}>{v.placa}</strong>
                <span className={`badge badge-${v.estado}`}>{v.estado}</span>
              </div>
              <p style={{ color: '#4b5563', margin: '0.5rem 0' }}>{v.tipo}</p>
              {v.fallas_criticas > 0 && (
                <small style={{ color: '#dc2626', display: 'block', marginBottom: '0.5rem' }}>
                  ⚠️ Falla crítica reportada (RN13)
                </small>
              )}
              <button
                className="btn-primary"
                style={{ backgroundColor: v.estado === 'BLOQUEADO' ? '#991b1b' : '#16794c' }}
                onClick={() => handleReservar(v.id_vehiculo)}
              >
                {v.estado === 'BLOQUEADO' ? 'Probar reserva (Disparar RN13)' : 'Confirmar reservación'}
              </button>
            </div>
          ))}
        </div>

        <h3 style={{ marginTop: '2.5rem' }}>Reservaciones persistidas en IBM Db2</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Vehículo</th>
              <th>Usuario</th>
              <th>Inicio</th>
              <th>Expira (RN4)</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {reservaciones.length === 0 ? (
              <tr><td colSpan="6" style={{ textAlign: 'center', color: '#6b7280' }}>Aún no hay reservaciones registradas.</td></tr>
            ) : (
              reservaciones.map((r) => (
                <tr key={r.id_reservacion}>
                  <td>#{r.id_reservacion}</td>
                  <td><strong>{r.placa}</strong></td>
                  <td>{r.usuario_email}</td>
                  <td>{r.inicio}</td>
                  <td>{r.expira}</td>
                  <td><span className="badge badge-DISPONIBLE">{r.estado}</span></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </main>
    </div>
  );
}
