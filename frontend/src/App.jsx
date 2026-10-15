import { useState, useEffect, useCallback } from 'react';
import './App.css';

// Configuración dinámica de API Base URL:
// Si se ejecuta en Vite dev server (puerto 5173), apunta al puerto 8000 del mismo host.
// Si se ejecuta servido por FastAPI (puerto 8000 u offline/móvil), usa rutas relativas ('/api/...').
const API_BASE = (typeof window !== 'undefined' && window.location.port === '5173')
  ? `http://${window.location.hostname || '127.0.0.1'}:8000`
  : '';


// 1. COMPONENTE: GESTIÓN DE USUARIOS (Crear, Consultar, Modificar, Eliminar)
function UserManagement() {
  const [users, setUsers] = useState([]);
  const [editingUser, setEditingUser] = useState(null); // Usuario en edición
  const [newUsername, setNewUsername] = useState('');
  const [newNombre, setNewNombre] = useState('');
  const [newRole, setNewRole] = useState('consultor');
  const [newPassword, setNewPassword] = useState('');

  // Estados para creación de nuevo usuario
  const [createCedula, setCreateCedula] = useState('');
  const [createNombre, setCreateNombre] = useState('');
  const [createRole, setCreateRole] = useState('consultor');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchUsers = () => {
    fetch(`${API_BASE}/api/admin/users`)
      .then(res => res.json())
      .then(data => setUsers(data))
      .catch(err => console.error("Error cargando usuarios:", err));
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    const cedulaLimpia = createCedula.trim();
    const nombreLimpio = createNombre.trim();

    if (!cedulaLimpia) {
      alert("Por favor ingrese el número de cédula.");
      return;
    }

    if (!/^\d+$/.test(cedulaLimpia)) {
      alert("La cédula debe contener únicamente números.");
      return;
    }

    if (cedulaLimpia.length < 5) {
      alert("La cédula debe tener al menos 5 dígitos.");
      return;
    }

    if (!nombreLimpio) {
      alert("Por favor ingrese el nombre completo del usuario.");
      return;
    }

    // Verificar si ya existe en la lista cargada
    const yaExiste = users.find(u => u.username === cedulaLimpia);
    if (yaExiste) {
      alert(`Ya existe un usuario registrado con la cédula ${cedulaLimpia}.`);
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/api/admin/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cedula: cedulaLimpia, nombre: nombreLimpio, role: createRole })
      });

      const data = await res.json();
      if (res.ok) {
        alert(`✅ Usuario creado exitosamente.\n\n• Nombre: ${nombreLimpio}\n• Cédula (Usuario): ${cedulaLimpia}\n• Rol: ${createRole}\n• Contraseña inicial por defecto: ${cedulaLimpia}`);
        setCreateCedula('');
        setCreateNombre('');
        setCreateRole('consultor');
        fetchUsers();
      } else {
        alert(data.detail || "Error al crear el usuario.");
      }
    } catch (err) {
      console.error("Error creando usuario:", err);
      alert("Error de conexión al intentar crear el usuario.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const deleteUser = async (id) => {
    if (!window.confirm("¿Estás seguro de eliminar este usuario?")) return;
    try {
      const res = await fetch(`${API_BASE}/api/admin/users/${id}`, { method: 'DELETE' });
      if (res.ok) {
        fetchUsers();
      } else {
        alert("Error al eliminar usuario.");
      }
    } catch (err) {
      console.error("Error al eliminar usuario:", err);
    }
  };

  const startEdit = (user) => {
    setEditingUser(user.id);
    setNewUsername(user.username);
    setNewNombre(user.nombre || '');
    setNewRole(user.role);
    setNewPassword(''); // Vacío por seguridad
  };

  const saveEdit = async (id) => {
    const cedulaLimpia = newUsername.trim();
    if (!cedulaLimpia || !/^\d+$/.test(cedulaLimpia)) {
      alert("La cédula/usuario debe contener únicamente números.");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/admin/users/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: cedulaLimpia, nombre: newNombre.trim(), role: newRole, password: newPassword })
      });
      if (res.ok) {
        alert("Usuario actualizado correctamente");
        setEditingUser(null);
        fetchUsers();
      } else {
        const data = await res.json();
        alert(data.detail || "Error al actualizar usuario");
      }
    } catch (err) {
      console.error("Error:", err);
      alert("Error de conexión al intentar actualizar el usuario.");
    }
  };

  // Estado para la búsqueda de usuarios
  const [userSearchQuery, setUserSearchQuery] = useState('');

  const filteredUsers = users.filter(user => {
    const q = userSearchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      user.username.toLowerCase().includes(q) ||
      (user.nombre && user.nombre.toLowerCase().includes(q))
    );
  });

  return (
    <div>
      <h3 style={{ color: '#0f172a', marginBottom: '8px', fontSize: '22px' }}>Configuración y Gestión de Usuarios</h3>
      <p style={{ color: '#64748b', marginBottom: '25px', fontSize: '14px' }}>
        Crea nuevos usuarios ingresando su nombre completo y cédula como identificador y clave inicial, o administra los accesos existentes.
      </p>

      {/* Formulario de Creación de Usuario */}
      <div style={{ background: '#ffffff', padding: '24px 28px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)', marginBottom: '30px' }}>
        <h4 style={{ color: '#047857', marginBottom: '18px', fontSize: '16px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
          ➕ Crear Nuevo Usuario
        </h4>
        <form onSubmit={handleCreateUser} style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ flex: '1 1 200px' }}>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>
              Número de Cédula (Único):
            </label>
            <input
              type="text"
              placeholder="Ej: 1035000123"
              value={createCedula}
              onChange={(e) => setCreateCedula(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', boxSizing: 'border-box', outline: 'none' }}
              required
            />
          </div>

          <div style={{ flex: '1 1 240px' }}>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>
              Nombre Completo:
            </label>
            <input
              type="text"
              placeholder="Ej: John Jairo Duque Zuluaga"
              value={createNombre}
              onChange={(e) => setCreateNombre(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', boxSizing: 'border-box', outline: 'none' }}
              required
            />
          </div>

          <div style={{ flex: '1 1 160px' }}>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>
              Rol de Acceso:
            </label>
            <select
              value={createRole}
              onChange={(e) => setCreateRole(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', boxSizing: 'border-box', outline: 'none' }}
            >
              <option value="consultor">Consultor</option>
              <option value="administrador">Administrador</option>
            </select>
          </div>

          <div style={{ flex: '0 0 auto' }}>
            <button
              type="submit"
              disabled={isSubmitting}
              style={{ padding: '10px 22px', background: '#047857', color: 'white', border: '1px solid #059669', borderRadius: '6px', fontWeight: '700', cursor: 'pointer', height: '41px', boxShadow: '0 2px 6px rgba(4, 120, 87, 0.2)' }}
            >
              {isSubmitting ? 'Guardando...' : 'Crear Usuario'}
            </button>
          </div>
        </form>

        <div style={{ marginTop: '14px', fontSize: '12px', color: '#854d0e', background: '#fefce8', border: '1px solid #fde047', padding: '10px 14px', borderRadius: '6px' }}>
          💡 <strong>Regla del sistema:</strong> El número de cédula será el usuario de acceso y la <strong>contraseña inicial por defecto</strong>. El usuario podrá conservarla o actualizarla posteriormente.
        </div>
      </div>

      {/* Encabezado con Búsqueda de Usuarios */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', flexWrap: 'wrap', gap: '15px' }}>
        <h4 style={{ color: '#0f172a', fontSize: '17px', fontWeight: '700', margin: 0 }}>
          Usuarios Registrados en el Sistema ({filteredUsers.length})
        </h4>
        
        <div style={{ display: 'flex', gap: '8px', maxWidth: '380px', width: '100%' }}>
          <input
            type="text"
            placeholder="🔍 Buscar por nombre o cédula..."
            value={userSearchQuery}
            onChange={(e) => setUserSearchQuery(e.target.value)}
            style={{ flex: 1, padding: '9px 14px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', outline: 'none', background: '#ffffff', color: '#0f172a' }}
          />
          <button
            type="button"
            style={{ padding: '9px 15px', background: '#047857', color: 'white', border: 'none', borderRadius: '6px', fontSize: '13px', fontWeight: '700', cursor: 'pointer' }}
          >
            Buscar
          </button>
          {userSearchQuery && (
            <button
              type="button"
              onClick={() => setUserSearchQuery('')}
              style={{ padding: '9px 12px', background: '#64748b', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', cursor: 'pointer', fontWeight: '600' }}
            >
              Limpiar
            </button>
          )}
        </div>
      </div>

      {/* Listado de Usuarios */}
      <div style={{ overflowX: 'auto', background: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#ecfdf5', textAlign: 'left', borderBottom: '2px solid #047857' }}>
              <th style={{ padding: '14px 18px', color: '#064e3b', fontSize: '14px', fontWeight: '700' }}>Cédula (Usuario)</th>
              <th style={{ padding: '14px 18px', color: '#064e3b', fontSize: '14px', fontWeight: '700' }}>Nombre Completo</th>
              <th style={{ padding: '14px 18px', color: '#064e3b', fontSize: '14px', fontWeight: '700' }}>Rol</th>
              <th style={{ padding: '14px 18px', color: '#064e3b', fontSize: '14px', fontWeight: '700', textAlign: 'center' }}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.length === 0 ? (
              <tr><td colSpan="4" style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>No se encontraron usuarios registrados {userSearchQuery ? `para "${userSearchQuery}"` : ''}.</td></tr>
            ) : (
              filteredUsers.map(user => (
                <tr key={user.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                  {editingUser === user.id ? (
                    <>
                      <td style={{ padding: '12px 18px' }}>
                        <input
                          type="text"
                          value={newUsername}
                          onChange={(e) => setNewUsername(e.target.value.replace(/\D/g, ''))}
                          placeholder="Cédula"
                          style={{ padding: '8px 10px', background: '#ffffff', color: '#0f172a', border: '1px solid #047857', borderRadius: '6px', width: '100%' }}
                        />
                      </td>
                      <td style={{ padding: '12px 18px' }}>
                        <input
                          type="text"
                          value={newNombre}
                          onChange={(e) => setNewNombre(e.target.value)}
                          placeholder="Nombre Completo"
                          style={{ padding: '8px 10px', background: '#ffffff', color: '#0f172a', border: '1px solid #047857', borderRadius: '6px', width: '100%' }}
                        />
                      </td>
                      <td style={{ padding: '12px 18px' }}>
                        <select
                          value={newRole}
                          onChange={(e) => setNewRole(e.target.value)}
                          style={{ padding: '8px 10px', background: '#ffffff', color: '#0f172a', border: '1px solid #047857', borderRadius: '6px' }}
                        >
                          <option value="administrador">administrador</option>
                          <option value="consultor">consultor</option>
                        </select>
                        <input
                          type="password"
                          placeholder="Nueva contraseña (opcional)"
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          style={{ marginTop: '6px', padding: '6px 10px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', borderRadius: '4px', width: '100%', fontSize: '12px' }}
                        />
                      </td>
                      <td style={{ padding: '12px 18px', textAlign: 'center' }}>
                        <button onClick={() => saveEdit(user.id)} style={{ background: '#047857', color: 'white', border: 'none', padding: '7px 14px', borderRadius: '6px', cursor: 'pointer', marginRight: '8px', fontWeight: '600' }}>Guardar</button>
                        <button onClick={() => setEditingUser(null)} style={{ background: '#64748b', color: 'white', border: 'none', padding: '7px 14px', borderRadius: '6px', cursor: 'pointer', fontWeight: '600' }}>Cancelar</button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td style={{ padding: '14px 18px', color: '#0f172a', fontWeight: '600' }}>{user.username}</td>
                      <td style={{ padding: '14px 18px', color: '#334155' }}>{user.nombre || '—'}</td>
                      <td style={{ padding: '14px 18px' }}>
                        <span style={{ padding: '4px 10px', borderRadius: '20px', background: user.role === 'administrador' ? '#ecfdf5' : '#fefce8', border: user.role === 'administrador' ? '1px solid #a7f3d0' : '1px solid #fde047', color: user.role === 'administrador' ? '#047857' : '#854d0e', fontSize: '12px', fontWeight: '700', textTransform: 'capitalize' }}>
                          {user.role}
                        </span>
                      </td>
                      <td style={{ padding: '14px 18px', textAlign: 'center' }}>
                        <button onClick={() => startEdit(user)} style={{ backgroundColor: '#0284c7', color: 'white', border: 'none', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', marginRight: '8px', fontWeight: '600' }}>Editar</button>
                        <button onClick={() => deleteUser(user.id)} style={{ backgroundColor: '#ef4444', color: 'white', border: 'none', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '600' }}>Eliminar</button>
                      </td>
                    </>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// 2. COMPONENTE: CARGUE DE INFORMACIÓN (Matriculados vs Graduados con validaciones y control de errores)
function UploadView() {
  const [tipoCargue, setTipoCargue] = useState('matriculados'); // 'matriculados' o 'graduados'
  const [file, setFile] = useState(null);
  const [loadsHistory, setLoadsHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Estado para la búsqueda en el historial de cargues
  const [loadSearchQuery, setLoadSearchQuery] = useState('');

  const fetchLoads = () => {
    fetch(`${API_BASE}/api/admin/loads`)
      .then(res => res.json())
      .then(data => setLoadsHistory(data))
      .catch(err => console.error("Error cargando historial:", err));
  };

  useEffect(() => {
    fetchLoads();
  }, []);

  // Función para calcular dinámicamente el Siguiente Periodo Requerido (1-2018 a 2-2070)
  const getNextExpectedPeriod = (history, tipo) => {
    const loaded = new Set(
      history.filter(item => item.tipo === tipo).map(item => item.periodo)
    );
    let year = 2018;
    let sem = 1;
    while (year <= 2070) {
      const code1 = `${sem}-${year}`;
      const code2 = `${year}-${sem}`;
      const code3 = `${year}`;
      if (!loaded.has(code1) && !loaded.has(code2) && !loaded.has(code3)) {
        return code1;
      }
      if (sem === 1) {
        sem = 2;
      } else {
        sem = 1;
        year += 1;
      }
    }
    return '2-2070';
  };

  const currentRequiredPeriod = getNextExpectedPeriod(loadsHistory, tipoCargue);

  const filteredLoads = loadsHistory.filter(load => {
    const q = loadSearchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      load.periodo.toLowerCase().includes(q) ||
      load.tipo.toLowerCase().includes(q) ||
      (load.archivo_nombre && load.archivo_nombre.toLowerCase().includes(q))
    );
  });

  const handleDeleteLoad = async (id) => {
    if (!window.confirm("¿Seguro que deseas eliminar este cargue? Esto te permitirá volver a subir este periodo.")) return;
    try {
      const res = await fetch(`${API_BASE}/api/admin/loads/${id}`, { method: 'DELETE' });
      if (res.ok) {
        alert("Cargue eliminado con éxito.");
        fetchLoads();
      }
    } catch (err) {
      console.error("Error:", err);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Debes seleccionar un archivo para cargar.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("tipo", tipoCargue);
    formData.append("periodo", currentRequiredPeriod);

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/admin/upload-period`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok) {
        if (data.status === 'new_program_prompt') {
          const confirmAdd = window.confirm(
            `⚠️ DETECCION DE NUEVO PROGRAMA ACADÉMICO:\n\nSe detectó el programa no registrado: '${data.new_program}'.\n\n¿Deseas confirmarlo y agregarlo permanentemente al directorio oficial de la UCO?`
          );
          if (confirmAdd) {
            const confRes = await fetch(`${API_BASE}/api/admin/confirm-new-program`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ program_name: data.new_program })
            });
            const confData = await confRes.json();
            if (confRes.ok) {
              alert(`✅ ${confData.message}`);
              
              // Re-intentar la subida con confirm_new_program = true
              const retryData = new FormData();
              retryData.append("file", file);
              retryData.append("tipo", tipoCargue);
              retryData.append("periodo", currentRequiredPeriod);
              retryData.append("confirm_new_program", "true");

              const retryRes = await fetch(`${API_BASE}/api/admin/upload-period`, {
                method: 'POST',
                body: retryData
              });
              const retryJson = await retryRes.json();
              if (retryRes.ok) {
                alert(`✅ ${retryJson.message}\nRegistros procesados: ${retryJson.total_rows}`);
                setFile(null);
                const fileInput = document.getElementById("file-upload-input");
                if (fileInput) fileInput.value = "";
                fetchLoads();
              } else {
                alert(retryJson.detail || "Error al procesar el archivo tras confirmación.");
              }
            }
          } else {
            alert("⚠️ Carga cancelada. El nuevo programa no fue registrado.");
          }
          return;
        }

        alert(`✅ ${data.message}\nRegistros procesados: ${data.total_rows}`);
        setFile(null);
        const fileInput = document.getElementById("file-upload-input");
        if (fileInput) fileInput.value = "";
        fetchLoads();

        alert(`ℹ️ Siguiente periodo habilitado secuencialmente: ${data.next_expected_period}`);
      } else {
        alert(data.detail || "Error al procesar el archivo.");
      }
    } catch (err) {
      console.error("Error:", err);
      alert("Error de conexión con el servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3 style={{ color: '#0f172a', marginBottom: '8px', fontSize: '22px' }}>Cargue de Información Institucional</h3>
      <p style={{ color: '#64748b', marginBottom: '25px', fontSize: '14px' }}>
        Sube la información respetando estrictamente la secuencia cronológica consecutiva (1-2018 a 2-2070).
      </p>

      {/* Formulario de Cargue */}
      <div style={{ background: '#ffffff', padding: '28px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)', marginBottom: '30px' }}>
        <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '540px' }}>
          <div>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>Tipo de Información:</label>
            <select
              value={tipoCargue}
              onChange={(e) => setTipoCargue(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', outline: 'none' }}
            >
              <option value="matriculados">Estudiantes Matriculados (Por Semestre 1-2018 a 2-2070)</option>
              <option value="graduados">Estudiantes Graduados (Por Semestre 1-2018 a 2-2070)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>
              Periodo Semestre a Cargar (Secuencia Estricta):
            </label>
            <select
              value={currentRequiredPeriod}
              disabled={true}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#ecfdf5', color: '#047857', fontWeight: '700', border: '1px solid #10b981', boxSizing: 'border-box' }}
            >
              <option value={currentRequiredPeriod}>
                {currentRequiredPeriod} (Periodo Siguiente Requerido)
              </option>
            </select>
            <div style={{ marginTop: '10px', fontSize: '12px', color: '#854d0e', background: '#fefce8', border: '1px solid #fde047', padding: '10px 14px', borderRadius: '6px' }}>
              📌 <strong>Control de Secuencia:</strong> Se muestra y exige únicamente el periodo consecutivo pendiente por cargar (comenzando en <strong>1-2018</strong>). Tras completar el cargue de este archivo, la lista habilitará automáticamente el siguiente periodo (ej: 1-2018 ➔ 2-2018 ➔ 1-2019).
            </div>
          </div>

          <div>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>Archivo (.csv, .xls, .xlsx):</label>
            <input
              id="file-upload-input"
              type="file"
              accept=".csv, .xls, .xlsx"
              onChange={(e) => setFile(e.target.files[0])}
              style={{ color: '#0f172a', padding: '10px', background: '#ffffff', borderRadius: '6px', border: '1px solid #cbd5e1', width: '100%', boxSizing: 'border-box' }}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{ padding: '12px', background: '#047857', color: 'white', border: 'none', borderRadius: '6px', fontWeight: '700', cursor: 'pointer', marginTop: '5px', boxShadow: '0 4px 12px rgba(4, 120, 87, 0.2)' }}
          >
            {loading ? "Procesando e ingresando archivo..." : `Cargar Periodo ${currentRequiredPeriod}`}
          </button>
        </form>
      </div>

      {/* Historial de Cargues con Buscador */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', flexWrap: 'wrap', gap: '15px' }}>
        <h4 style={{ color: '#0f172a', fontSize: '17px', fontWeight: '700', margin: 0 }}>
          Historial de Periodos Cargados ({filteredLoads.length})
        </h4>

        <div style={{ display: 'flex', gap: '8px', maxWidth: '380px', width: '100%' }}>
          <input
            type="text"
            placeholder="🔍 Buscar en historial por periodo, tipo o archivo..."
            value={loadSearchQuery}
            onChange={(e) => setLoadSearchQuery(e.target.value)}
            style={{ flex: 1, padding: '9px 14px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', outline: 'none', background: '#ffffff', color: '#0f172a' }}
          />
          <button
            type="button"
            style={{ padding: '9px 15px', background: '#047857', color: 'white', border: 'none', borderRadius: '6px', fontSize: '13px', fontWeight: '700', cursor: 'pointer' }}
          >
            Buscar
          </button>
          {loadSearchQuery && (
            <button
              type="button"
              onClick={() => setLoadSearchQuery('')}
              style={{ padding: '9px 12px', background: '#64748b', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', cursor: 'pointer', fontWeight: '600' }}
            >
              Limpiar
            </button>
          )}
        </div>
      </div>

      <div style={{ overflowX: 'auto', background: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#ecfdf5', textAlign: 'left', borderBottom: '2px solid #047857' }}>
              <th style={{ padding: '14px 18px', color: '#064e3b', fontSize: '14px', fontWeight: '700' }}>Tipo</th>
              <th style={{ padding: '14px 18px', color: '#064e3b', fontSize: '14px', fontWeight: '700' }}>Periodo / Año</th>
              <th style={{ padding: '14px 18px', color: '#064e3b', fontSize: '14px', fontWeight: '700' }}>Archivo Original</th>
              <th style={{ padding: '14px 18px', color: '#064e3b', fontSize: '14px', fontWeight: '700', textAlign: 'center' }}>Acción de Corrección</th>
            </tr>
          </thead>
          <tbody>
            {filteredLoads.length === 0 ? (
              <tr><td colSpan="4" style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>No se encontraron registros de cargue {loadSearchQuery ? `para "${loadSearchQuery}"` : ''}.</td></tr>
            ) : (
              filteredLoads.map(load => (
                <tr key={load.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                  <td style={{ padding: '14px 18px', color: '#0f172a', textTransform: 'capitalize', fontWeight: '500' }}>{load.tipo}</td>
                  <td style={{ padding: '14px 18px', color: '#047857', fontWeight: '700' }}>{load.periodo}</td>
                  <td style={{ padding: '14px 18px', color: '#475569' }}>{load.archivo_nombre}</td>
                  <td style={{ padding: '14px 18px', textAlign: 'center' }}>
                    <button
                      onClick={() => handleDeleteLoad(load.id)}
                      style={{ backgroundColor: '#ef4444', color: 'white', border: 'none', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px', fontWeight: '600' }}
                      title="Elimina este registro si el archivo tenía errores y necesitas subir otro"
                    >
                      Eliminar / Re-subir
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Array global de todos los programas oficiales de la UCO (según documento Codificación de Programas)
const ALL_UCO_PROGRAMS = [
  'Administración de Empresas',
  'Agronomía',
  'Comercio Exterior',
  'Comunicación Social',
  'Contaduría Pública',
  'Derecho',
  'Derecho y Ciencias Sociales',
  'Enfermería',
  'Gerontología',
  'Ingeniería Ambiental',
  'Ingeniería Electrónica',
  'Ingeniería Industrial',
  'Ingeniería de Sistemas',
  'Licenciatura en Ciencias Naturales',
  'Licenciatura en Educación Básica (Ed. Religiosa)',
  'Licenciatura en Educación Campesina y Rural',
  'Licenciatura en Educación Física, Recreación y Deportes',
  'Licenciatura en Educación Religiosa',
  'Licenciatura en Filosofía',
  'Licenciatura en Filosofía y Educación Religiosa',
  'Licenciatura en Lenguas Extranjeras',
  'Licenciatura en Lenguas Extranjeras (Énfasis Inglés)',
  'Licenciatura en Matemáticas',
  'Licenciatura en Primera Infancia',
  'Maestría en Educación',
  'Maestría en Educación Virtual',
  'Maestría en Humanidades',
  'Maestría en Psicología',
  'Maestría en Salud Familiar',
  'Maestría en Sanidad Vegetal',
  'Maestría en Tributación',
  'Nutrición y Dietética',
  'Psicología',
  'Tecnología Agropecuaria',
  'Tecnología en Operaciones Financieras',
  'Teología',
  'Teología Virtual UCN',
  'Trabajo Social',
  'Técnico Profesional en Programación Web',
  'Zootecnia',
  'Especializaciones y Posgrados UCO'
];

// 3. COMPONENTE: INDICADORES Y ESTADÍSTICAS (5 Indicadores Oficiales SPADIES 3.0)
function IndicatorsView() {
  const [selectedIndicator, setSelectedIndicator] = useState('TDA'); // TDA, TDC, TDPA, TGA, TAI
  const [selectedPrograms, setSelectedPrograms] = useState([...ALL_UCO_PROGRAMS]);
  const [programSearchText, setProgramSearchText] = useState('');
  const [isMultiSelectExpanded, setIsMultiSelectExpanded] = useState(false);
  const [loadsHistory, setLoadsHistory] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/admin/loads`)
      .then(res => res.json())
      .then(data => setLoadsHistory(data))
      .catch(err => console.error("Error cargando historial de cargas:", err));
  }, []);

  const toggleProgram = (progName) => {
    if (selectedPrograms.includes(progName)) {
      setSelectedPrograms(selectedPrograms.filter(p => p !== progName));
    } else {
      setSelectedPrograms([...selectedPrograms, progName]);
    }
  };

  const selectAllPrograms = () => {
    setSelectedPrograms([...ALL_UCO_PROGRAMS]);
  };

  const deselectAllPrograms = () => {
    setSelectedPrograms([]);
  };

  const isAllSelected = selectedPrograms.length === ALL_UCO_PROGRAMS.length;

  const filteredProgramList = ALL_UCO_PROGRAMS.filter(p => 
    !programSearchText || p.toLowerCase().includes(programSearchText.toLowerCase())
  );

  // Metadatos de la fórmula matemática de los 5 indicadores según imágenes y documentación SPADIES 3.0
  const indicatorDetails = {
    TDA: {
      title: 'Tasa de Deserción Anual (TDA)',
      formulaText: 'TDA_t = ( Desertores de t / Matriculados en t - 2 ) * 100',
      description: 'Mide la proporción de estudiantes que cayeron en deserción en el periodo evaluado (t) respecto a los matriculados dos periodos académicos atrás (t - 2).',
      variableNote: 'Donde t es el periodo evaluado.',
      numerator: 'Desertores de t (estudiantes matriculados en t-2 no matriculados en t-1 ni t)',
      denominator: 'Matriculados en t - 2 (un año antes)',
      focus: 'Deserción de Corto Plazo / Evaluación Anual'
    },
    TDC: {
      title: 'Tasa de Deserción por Cohorte (TDC)',
      formulaText: 'TDC_{c,s} = ( ∑_{s=1}^S Desertores_{c,s} / Primíparos_c ) * 100',
      description: 'Evalúa la acumulación progresiva de deserción para una cohorte de ingreso específica (c) a lo largo de sus semestres de permanencia (s).',
      variableNote: 'Donde c es la cohorte de ingreso y s el semestre de trayectoria.',
      numerator: 'Suma acumulada de desertores de la cohorte c hasta el semestre S',
      denominator: 'Primíparos de la cohorte c (estudiantes de primer curso)',
      focus: 'Seguimiento Longitudinal por Cohorte'
    },
    TDPA: {
      title: 'Tasa de Deserción Promedio Acumulada (TDPA)',
      formulaText: 'TDPA_s = ( ∑_{c=1}^C ∑_{s=1}^S Desertores_{c,s} / ∑_{c=1}^C Primíparos_c ) * 100',
      description: 'Mide la deserción acumulada promedio global considerando todas las cohortes de ingreso (c = 1 ... C) hasta el semestre de trayectoria (s).',
      variableNote: 'Donde c es la cohorte y s el semestre.',
      numerator: 'Suma total de desertores de todas las cohortes hasta el semestre s',
      denominator: 'Suma total de primíparos de todas las cohortes C',
      focus: 'Tendencia Estructural e Institucional'
    },
    TGA: {
      title: 'Tasa de Graduación Acumulada (TGA)',
      formulaText: 'TGA_s = ( ∑_{c=1}^C ∑_{s=1}^S Graduados_{c,s} / ∑_{c=1}^C Primíparos_c ) * 100',
      description: 'Indica la proporción acumulada de estudiantes que han completado exitosamente su plan de estudios y obtenido título hasta el semestre s.',
      variableNote: 'Donde c es la cohorte y s el semestre.',
      numerator: 'Suma acumulada de estudiantes graduados de las cohortes C hasta el semestre s',
      denominator: 'Suma total de primíparos de todas las cohortes C',
      focus: 'Eficacia Institucional y Titulación'
    },
    TAI: {
      title: 'Tasa de Ausencia Intersemestral (TAI)',
      formulaText: 'TAI_t = ( Ausentes_t / Matriculados_{t-1} ) * 100',
      description: 'Mide la proporción de estudiantes que estando matriculados en el periodo anterior (t - 1) no registraron matrícula en el periodo actual (t).',
      variableNote: 'Donde t es el periodo actual evaluado.',
      numerator: 'Ausentes en el periodo t (no matricularon respecto a t-1)',
      denominator: 'Matriculados en el periodo anterior (t - 1)',
      focus: 'Alerta Temprana y Riesgo de Retiro Inminente'
    }
  };

  const currentDetail = indicatorDetails[selectedIndicator];

  return (
    <div>
      <h3 style={{ color: '#0f172a', marginBottom: '8px', fontSize: '22px' }}>Indicadores y Estadísticas Institucionales</h3>
      <p style={{ color: '#64748b', marginBottom: '25px', fontSize: '14px' }}>
        Filtra y analiza los 5 indicadores estándar definidos por la metodología <strong>SPADIES 3.0</strong> y la Dirección Académica UCO.
      </p>

      {/* Panel de Filtros con Multi-Selección de Programas */}
      <div style={{ background: '#ffffff', padding: '22px 25px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)', marginBottom: '25px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', alignItems: 'flex-start' }}>
          
          {/* 1. Seleccionar Indicador */}
          <div style={{ flex: '1 1 300px' }}>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '700' }}>
              Seleccionar Indicador SPADIES 3.0:
            </label>
            <select
              value={selectedIndicator}
              onChange={(e) => setSelectedIndicator(e.target.value)}
              style={{ width: '100%', padding: '11px 14px', borderRadius: '6px', background: '#ecfdf5', color: '#047857', border: '1px solid #047857', fontWeight: '700', outline: 'none' }}
            >
              <option value="TDA">Tasa de Deserción Anual (TDA)</option>
              <option value="TDC">Tasa de Deserción por Cohorte (TDC)</option>
              <option value="TDPA">Tasa de Deserción Promedio Acumulada (TDPA)</option>
              <option value="TGA">Tasa de Graduación Acumulada (TGA)</option>
              <option value="TAI">Tasa de Ausencia Intersemestral (TAI)</option>
            </select>
          </div>

          {/* 2. Seleccionar Programas (Multi-Selección) */}
          <div style={{ flex: '2 1 450px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <label style={{ color: '#475569', fontSize: '13px', fontWeight: '700' }}>
                Filtro Multiprograma ({selectedPrograms.length} de {ALL_UCO_PROGRAMS.length} seleccionados):
              </label>
              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  type="button"
                  onClick={selectAllPrograms}
                  style={{ padding: '4px 10px', fontSize: '11px', background: isAllSelected ? '#047857' : '#f1f5f9', color: isAllSelected ? '#ffffff' : '#334155', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer', fontWeight: '700' }}
                >
                  🏛️ Seleccionar Todos ({ALL_UCO_PROGRAMS.length})
                </button>
                <button
                  type="button"
                  onClick={deselectAllPrograms}
                  style={{ padding: '4px 10px', fontSize: '11px', background: '#f1f5f9', color: '#64748b', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer', fontWeight: '600' }}
                >
                  🧹 Limpiar
                </button>
              </div>
            </div>

            {/* Caja desplegable interactiva */}
            <button
              type="button"
              onClick={() => setIsMultiSelectExpanded(!isMultiSelectExpanded)}
              style={{ width: '100%', padding: '11px 14px', borderRadius: '6px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', outline: 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', textAlign: 'left' }}
            >
              <span style={{ fontSize: '13px', fontWeight: '600', color: selectedPrograms.length === 0 ? '#b91c1c' : '#047857' }}>
                {isAllSelected
                  ? '🏛️ Toda la Universidad (Global UCO - 30 Programas)'
                  : selectedPrograms.length === 0
                  ? '⚠️ Ningún programa seleccionado (Haz clic para seleccionar)'
                  : `🎓 Multiprograma: ${selectedPrograms.length} programa(s) seleccionado(s)`
                }
              </span>
              <span style={{ fontSize: '12px', color: '#64748b' }}>
                {isMultiSelectExpanded ? '▲ Ocultar lista' : '▼ Seleccionar/Modificar varios programas'}
              </span>
            </button>

            {/* Panel Expandible de Checkboxes */}
            {isMultiSelectExpanded && (
              <div style={{ marginTop: '10px', padding: '16px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #cbd5e1', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                
                {/* Buscador de programas */}
                <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="text"
                    placeholder="🔍 Buscar programas (ej. Sistemas, Derecho, Zootecnia)..."
                    value={programSearchText}
                    onChange={(e) => setProgramSearchText(e.target.value)}
                    style={{ flex: 1, padding: '7px 12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', outline: 'none', background: '#ffffff', color: '#0f172a' }}
                  />
                  {programSearchText && (
                    <button
                      type="button"
                      onClick={() => setProgramSearchText('')}
                      style={{ padding: '6px 10px', fontSize: '12px', background: '#cbd5e1', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      Limpiar
                    </button>
                  )}
                </div>

                {/* Cuadrícula de Checkboxes */}
                <div style={{ maxHeight: '220px', overflowY: 'auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '8px', paddingRight: '4px' }}>
                  {filteredProgramList.map(prog => {
                    const isChecked = selectedPrograms.includes(prog);
                    return (
                      <label
                        key={prog}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '7px 10px',
                          borderRadius: '6px',
                          border: isChecked ? '1px solid #047857' : '1px solid #e2e8f0',
                          background: isChecked ? '#ecfdf5' : '#ffffff',
                          cursor: 'pointer',
                          fontSize: '12px',
                          color: isChecked ? '#064e3b' : '#334155',
                          fontWeight: isChecked ? '700' : '500',
                          transition: 'all 0.15s ease'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleProgram(prog)}
                          style={{ accentColor: '#047857', cursor: 'pointer' }}
                        />
                        <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{prog}</span>
                      </label>
                    );
                  })}
                </div>

                {filteredProgramList.length === 0 && (
                  <p style={{ textAlign: 'center', color: '#64748b', fontSize: '13px', margin: '15px 0 5px 0' }}>
                    No se encontraron programas con "{programSearchText}".
                  </p>
                )}
              </div>
            )}

          </div>

        </div>
      </div>

      {/* Tarjeta de Fórmula Matemática y Documentación Técnica */}
      <div style={{ background: '#ffffff', padding: '28px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)', marginBottom: '25px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h4 style={{ color: '#047857', fontSize: '18px', fontWeight: '700', margin: 0 }}>
            📐 {currentDetail.title}
          </h4>
          <span style={{ background: '#fefce8', border: '1px solid #fde047', color: '#854d0e', fontSize: '12px', fontWeight: '700', padding: '4px 10px', borderRadius: '12px' }}>
            {currentDetail.focus}
          </span>
        </div>

        {/* Ecuación Renderizada */}
        <div style={{ background: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #cbd5e1', textAlign: 'center', marginBottom: '18px' }}>
          <div style={{ fontSize: '20px', fontFamily: 'Cambria, "Times New Roman", serif', fontWeight: 'bold', color: '#0f172a', letterSpacing: '0.5px' }}>
            {currentDetail.formulaText}
          </div>
          <div style={{ marginTop: '8px', fontSize: '13px', color: '#854d0e', fontStyle: 'italic', fontWeight: '600' }}>
            {currentDetail.variableNote}
          </div>
        </div>

        <p style={{ color: '#334155', fontSize: '14px', lineHeight: '1.6', marginBottom: '15px' }}>
          {currentDetail.description}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', background: '#ecfdf5', padding: '15px 18px', borderRadius: '8px', border: '1px solid #a7f3d0', fontSize: '13px' }}>
          <div>
            <strong style={{ color: '#064e3b' }}>Numerador:</strong> <span style={{ color: '#047857' }}>{currentDetail.numerator}</span>
          </div>
          <div>
        <strong style={{ color: '#064e3b' }}>Denominador:</strong> <span style={{ color: '#047857' }}>{currentDetail.denominator}</span>
          </div>
        </div>
      </div>

      {/* Visualización de Métricas y Tablas de Resultados SPADIES 3.0 */}
      <IndicatorTableResult selectedIndicator={selectedIndicator} selectedPrograms={selectedPrograms} allProgramsCount={ALL_UCO_PROGRAMS.length} loadsCount={loadsHistory.length} />
    </div>
  );
}

// Sub-componente para renderizar las tablas de resultados según la estructura de las imágenes SPADIES 3.0
function IndicatorTableResult({ selectedIndicator, selectedPrograms = [], allProgramsCount = 30, loadsCount = 0 }) {
  const [tableSearch, setTableSearch] = useState('');
  const [computedData, setComputedData] = useState(null);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  useEffect(() => {
    if (loadsCount > 0) {
      setLoadingMetrics(true);
      const progsParam = selectedPrograms.join(',');
      fetch(`${API_BASE}/api/admin/metrics/${selectedIndicator}?programs=${encodeURIComponent(progsParam)}`)
        .then(res => res.json())
        .then(data => {
          if (data && data.data) {
            setComputedData(data.data);
          }
        })
        .catch(err => console.error("Error cargando métricas:", err))
        .finally(() => setLoadingMetrics(false));
    } else {
      setComputedData(null);
    }
  }, [selectedIndicator, selectedPrograms, loadsCount]);

  // Generar resumen del alcance
  let scopeText = '';
  if (selectedPrograms.length === allProgramsCount) {
    scopeText = '🏛️ Toda la Universidad (Global UCO - Todos los Programas)';
  } else if (selectedPrograms.length === 0) {
    scopeText = '⚠️ Ningún programa seleccionado';
  } else if (selectedPrograms.length === 1) {
    scopeText = `🎓 Programa: ${selectedPrograms[0]}`;
  } else {
    scopeText = `🎓 Multiprograma (${selectedPrograms.length} programas): ${selectedPrograms.slice(0, 3).join(', ')}${selectedPrograms.length > 3 ? ` y ${selectedPrograms.length - 3} más` : ''}`;
  }

  const tdcColumns = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17'];
  const tdpaColumns = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17'];
  const tdaPeriods = (computedData && computedData.periods) ? computedData.periods : [];
  const tgaColumns = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17'];
  const taiPeriods = (computedData && computedData.periods) ? computedData.periods : [];

  // Datos reales calculados por el motor SPADIES según los períodos efectivamente cargados
  const tdcData = (computedData && Array.isArray(computedData)) ? computedData : [];

  const tdpaValues = (computedData && !Array.isArray(computedData) && !computedData.periods) ? 
    tdpaColumns.map(c => computedData[c] || '—') :
    tdpaColumns.map(() => '—');

  const tdaData = (computedData && computedData.rows) ? computedData.rows : [];

  const tgaValues = (computedData && !Array.isArray(computedData) && !computedData.periods) ?
    tgaColumns.map(c => computedData[c] || '—') :
    tgaColumns.map(() => '—');

  const taiData = (computedData && computedData.rows) ? computedData.rows : [];

  return (
    <div style={{ background: '#ffffff', padding: '25px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)', marginTop: '25px' }}>
      
      {/* Estado cuando NO hay archivos de datos cargados */}
      {loadsCount === 0 && (
        <div style={{ background: '#fefce8', border: '1px solid #fde047', borderRadius: '10px', padding: '24px 28px', textAlign: 'center', marginBottom: '22px' }}>
          <div style={{ fontSize: '30px', marginBottom: '8px' }}>📂</div>
          <h4 style={{ color: '#854d0e', fontSize: '17px', fontWeight: '700', marginBottom: '8px' }}>
            Aún no hay archivos de datos cargados para calcular {selectedIndicator}
          </h4>
          <p style={{ color: '#713f12', fontSize: '13px', maxWidth: '680px', margin: '0 auto 12px auto', lineHeight: '1.6' }}>
            Los valores y porcentajes de esta matriz se calcularán automáticamente cuando cargues los archivos Excel de estudiantes matriculados y graduados en la sección <strong>"Cargue de Información"</strong>.
          </p>
          <div style={{ display: 'inline-block', padding: '6px 14px', background: '#ffffff', border: '1px solid #eab308', borderRadius: '6px', fontSize: '12px', color: '#854d0e', fontWeight: '700' }}>
            📌 Vista previa de la plantilla en espera de archivos de datos
          </div>
        </div>
      )}

      {/* Encabezado del Reporte con Buscador estilo SPADIES */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '15px' }}>
        <div>
          <h4 style={{ color: '#0f172a', fontSize: '17px', fontWeight: '700', margin: 0 }}>
            📊 Matriz de Resultados {loadsCount > 0 ? 'Calculados' : '(Plantilla Esperando Cargue)'}: {selectedIndicator}
          </h4>
          <p style={{ color: '#64748b', fontSize: '13px', margin: '4px 0 0 0' }}>
            Alcance seleccionado: <strong>{scopeText}</strong>
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ color: '#475569', fontSize: '13px', fontWeight: '600' }}>Buscar:</label>
          <input
            type="text"
            placeholder="Filtrar en tabla..."
            value={tableSearch}
            onChange={(e) => setTableSearch(e.target.value)}
            style={{ padding: '7px 12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', outline: 'none', background: '#ffffff', width: '180px', color: '#0f172a' }}
          />
        </div>
      </div>

      {/* RENDERIZADO DE TABLAS SEGÚN INDICADOR */}
      
      {/* 1. TDC - Tasa de Deserción por Cohorte */}
      {selectedIndicator === 'TDC' && (
        <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'center' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1', color: '#475569' }}>
                <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: '700', borderRight: '1px solid #e2e8f0' }}>COHORTE ⇯</th>
                {tdcColumns.map(col => (
                  <th key={col} style={{ padding: '10px 8px', fontWeight: '700', minWidth: '55px', borderRight: '1px solid #f1f5f9' }}>{col} ⇯</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tdcData.length === 0 ? (
                <tr>
                  <td colSpan={tdcColumns.length + 1} style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>
                    {loadingMetrics ? '⏳ Calculando cohorte...' : 'No hay cohortes de matriculados cargadas en el sistema.'}
                  </td>
                </tr>
              ) : (
                tdcData
                  .filter(row => !tableSearch || row.cohorte.toLowerCase().includes(tableSearch.toLowerCase()))
                  .map((row, idx) => (
                    <tr key={row.cohorte} style={{ background: idx % 2 === 0 ? '#ffffff' : '#f9fafb', borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '10px 14px', textAlign: 'left', fontWeight: '700', color: '#0f172a', borderRight: '1px solid #e2e8f0' }}>{row.cohorte}</td>
                      {tdcColumns.map(col => (
                        <td key={col} style={{ padding: '10px 8px', color: loadsCount > 0 ? '#334155' : '#94a3b8', borderRight: '1px solid #f1f5f9' }}>
                          {loadsCount > 0 ? (row[col] || '—') : '—'}
                        </td>
                      ))}
                    </tr>
                  ))
              )}
            </tbody>
          </table>

          {tdcData.length > 0 && (
            <div style={{ padding: '12px 16px', background: '#f8fafc', borderTop: '1px solid #e2e8f0', fontSize: '12.5px', color: '#334155', lineHeight: '1.5' }}>
              💡 <strong>Regla metodológica SPADIES 3.0:</strong> En el semestre 1 (S1) de ingreso, la deserción es <strong>0.00%</strong> ya que la cohorte ingresa formalmente matriculada. Para declarar a un estudiante como desertor en semestres posteriores, el estándar SPADIES exige <strong>dos (2) períodos consecutivos sin matrícula</strong> ni graduación. Los semestres marcados con guion (<code>—</code>) corresponden a períodos académicos futuros que aún no han sido cargados al repositorio.
            </div>
          )}
        </div>
      )}

      {/* 2. TDPA - Tasa de Deserción Promedio Acumulada */}
      {selectedIndicator === 'TDPA' && (
        <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'center' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1', color: '#475569' }}>
                {tdpaColumns.map(col => (
                  <th key={col} style={{ padding: '10px 12px', fontWeight: '700', minWidth: '60px', borderRight: '1px solid #f1f5f9' }}>{col} ⇯</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr style={{ background: '#ffffff' }}>
                {tdpaValues.map((val, i) => (
                  <td key={i} style={{ padding: '14px 12px', color: loadsCount > 0 ? '#047857' : '#94a3b8', fontWeight: '700', borderRight: '1px solid #f1f5f9' }}>
                    {loadsCount > 0 ? val : '—'}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>

          <div style={{ padding: '12px 16px', background: '#f8fafc', borderTop: '1px solid #e2e8f0', fontSize: '12.5px', color: '#334155', lineHeight: '1.5' }}>
            📊 <strong>Ponderación institucional TDPA:</strong> Promedia la deserción de todas las cohortes cargadas para cada semestre de trayectoria. Los semestres en <code>—</code> indican que las cohortes cargadas aún no han alcanzado dicho semestre de trayectoria o no acumulan los 2 semestres consecutivos de ausencia requeridos.
          </div>
        </div>
      )}

      {/* 3. TDA - Tasa de Deserción Anual */}
      {selectedIndicator === 'TDA' && (
        <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'center' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1', color: '#475569' }}>
                <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: '700', minWidth: '150px', borderRight: '1px solid #e2e8f0' }}>TIPO ⇯</th>
                {tdaPeriods.length === 0 ? (
                  <th style={{ padding: '10px 10px', fontWeight: '700' }}>Sin períodos cargados</th>
                ) : (
                  tdaPeriods.map(p => (
                    <th key={p} style={{ padding: '10px 10px', fontWeight: '700', minWidth: '70px', borderRight: '1px solid #f1f5f9' }}>{p} ⇯</th>
                  ))
                )}
              </tr>
            </thead>
            <tbody>
              {tdaData.length === 0 || tdaPeriods.length === 0 ? (
                <tr>
                  <td colSpan={Math.max(2, tdaPeriods.length + 1)} style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>
                    {loadingMetrics ? '⏳ Calculando tasa anual...' : 'No hay períodos suficientes cargados para calcular la Tasa de Deserción Anual.'}
                  </td>
                </tr>
              ) : (
                tdaData
                  .filter(row => !tableSearch || row.tipo.toLowerCase().includes(tableSearch.toLowerCase()))
                  .map((row, idx) => (
                    <tr key={row.tipo} style={{ background: idx % 2 === 0 ? '#ffffff' : '#f9fafb', borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '12px 14px', textAlign: 'left', fontWeight: '700', color: row.tipo.includes('DESERCIÓN') ? '#b91c1c' : '#047857', borderRight: '1px solid #e2e8f0' }}>
                        {row.tipo}
                      </td>
                      {row.vals.map((v, i) => (
                        <td key={i} style={{ padding: '12px 10px', color: loadsCount > 0 ? '#334155' : '#94a3b8', borderRight: '1px solid #f1f5f9' }}>
                          {loadsCount > 0 ? v : '—'}
                        </td>
                      ))}
                    </tr>
                  ))
              )}
            </tbody>
          </table>

          <div style={{ padding: '12px 16px', background: '#eff6ff', borderTop: '1px solid #bfdbfe', fontSize: '12.5px', color: '#1e40af', lineHeight: '1.5' }}>
            ℹ️ <strong>Condición técnica SPADIES (TDA):</strong> Compara los estudiantes de un período <em>t</em> respecto a los matriculados dos semestres atrás (<em>t - 2</em>, un año completo). {tdaPeriods.length < 2 ? `Con solo ${tdaPeriods.length} período(s) cargado(s) (${tdaPeriods.join(', ') || 'ninguno'}), no existe período t-2 previo para comparar, por lo que el valor se muestra como no disponible ('—'). Al subir períodos posteriores (ej: 1-2019), el sistema calculará automáticamente la TDA respecto a ${tdaPeriods[0] || '1-2018'}.` : `Cálculo realizado comparando la retención respecto al período dos semestres anterior.`}
          </div>
        </div>
      )}

      {/* 4. TGA - Tasa de Graduación Acumulada */}
      {selectedIndicator === 'TGA' && (
        <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'center' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1', color: '#475569' }}>
                {tgaColumns.map(col => (
                  <th key={col} style={{ padding: '10px 12px', fontWeight: '700', minWidth: '60px', borderRight: '1px solid #f1f5f9' }}>{col} ⇯</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr style={{ background: '#ffffff' }}>
                {tgaValues.map((val, i) => (
                  <td key={i} style={{ padding: '14px 12px', color: loadsCount > 0 ? '#0284c7' : '#94a3b8', fontWeight: '700', borderRight: '1px solid #f1f5f9' }}>
                    {loadsCount > 0 ? val : '—'}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>

          <div style={{ padding: '12px 16px', background: '#f0fdfa', borderTop: '1px solid #99f6e4', fontSize: '12.5px', color: '#0f766e', lineHeight: '1.5' }}>
            🎓 <strong>Nota sobre graduación:</strong> La TGA mide el porcentaje acumulado de primíparos de una cohorte que han obtenido su título de graduación. Si aún no se han subido los archivos semestrales de <strong>Egresados / Graduados</strong> en el módulo "Cargue de Información", la tasa acumulada permanecerá en <strong>0.00%</strong> o <code>—</code>.
          </div>
        </div>
      )}

      {/* 5. TAI - Tasa de Ausencia Intersemestral */}
      {selectedIndicator === 'TAI' && (
        <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'center' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1', color: '#475569' }}>
                <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: '700', minWidth: '160px', borderRight: '1px solid #e2e8f0' }}>TIPO ⇯</th>
                {taiPeriods.length === 0 ? (
                  <th style={{ padding: '10px 10px', fontWeight: '700' }}>Sin períodos cargados</th>
                ) : (
                  taiPeriods.map(p => (
                    <th key={p} style={{ padding: '10px 10px', fontWeight: '700', minWidth: '70px', borderRight: '1px solid #f1f5f9' }}>{p} ⇯</th>
                  ))
                )}
              </tr>
            </thead>
            <tbody>
              {taiData.length === 0 || taiPeriods.length === 0 ? (
                <tr>
                  <td colSpan={Math.max(2, taiPeriods.length + 1)} style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>
                    {loadingMetrics ? '⏳ Calculando ausencia intersemestral...' : 'No hay períodos suficientes cargados para calcular la TAI.'}
                  </td>
                </tr>
              ) : (
                taiData
                  .filter(row => !tableSearch || row.tipo.toLowerCase().includes(tableSearch.toLowerCase()))
                  .map((row, idx) => (
                    <tr key={row.tipo} style={{ background: idx % 2 === 0 ? '#ffffff' : '#f9fafb', borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '12px 14px', textAlign: 'left', fontWeight: '700', color: row.tipo.includes('AUSENTISMO') ? '#d97706' : '#047857', borderRight: '1px solid #e2e8f0' }}>
                        {row.tipo}
                      </td>
                      {row.vals.map((v, i) => (
                        <td key={i} style={{ padding: '12px 10px', color: loadsCount > 0 ? '#334155' : '#94a3b8', borderRight: '1px solid #f1f5f9' }}>
                          {loadsCount > 0 ? v : '—'}
                        </td>
                      ))}
                    </tr>
                  ))
              )}
            </tbody>
          </table>

          <div style={{ padding: '12px 16px', background: '#fffbeb', borderTop: '1px solid #fde68a', fontSize: '12.5px', color: '#92400e', lineHeight: '1.5' }}>
            ⚠️ <strong>Condición técnica SPADIES (TAI):</strong> Compara los estudiantes matriculados en <em>t - 1</em> que no continuaron en el semestre inmediato <em>t</em>. {taiPeriods.length < 2 ? `Para el primer período cargado (${taiPeriods[0] || 'inicial'}), no existe período previo de referencia en la base de datos ('—').` : `Cálculo realizado comparando la continuidad entre semestres consecutivos.`}
          </div>
        </div>
      )}

      {/* Nota pie de página institucional */}
      <div style={{ marginTop: '16px', fontSize: '12px', color: '#64748b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>📌 <em>Estructura según estándar SPADIES 3.0 para la Universidad Católica de Oriente (UCO).</em></span>
        <span style={{ color: '#047857', fontWeight: '600' }}>UCO Analytics 2026</span>
      </div>
    </div>
  );
}

// 4. COMPONENTE: CAMBIAR CONTRASEÑA
function ChangePasswordView({ initialUsername = '', onSuccessBack = null }) {
  const [usernameInput, setUsernameInput] = useState(initialUsername);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialUsername) {
      setUsernameInput(initialUsername);
    }
  }, [initialUsername]);

  const handleChangePassword = async (e) => {
    e.preventDefault();
    const userClean = usernameInput.trim();

    if (!userClean) {
      alert("Por favor ingresa tu número de cédula / usuario.");
      return;
    }

    if (!oldPassword) {
      alert("Por favor ingresa la contraseña anterior.");
      return;
    }

    if (!newPassword) {
      alert("Por favor ingresa la nueva contraseña.");
      return;
    }

    if (newPassword.length < 4) {
      alert("La nueva contraseña debe tener al menos 4 caracteres.");
      return;
    }

    if (newPassword !== confirmPassword) {
      alert("La nueva contraseña y su confirmación no coinciden.");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_BASE}/api/change-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: userClean,
          old_password: oldPassword,
          new_password: newPassword
        })
      });

      const data = await response.json();
      if (response.ok) {
        alert("✅ Contraseña actualizada exitosamente.");
        setOldPassword('');
        setNewPassword('');
        setConfirmPassword('');
        if (onSuccessBack) onSuccessBack();
      } else {
        alert(data.detail || "Error al cambiar la contraseña.");
      }
    } catch (err) {
      console.error("Error cambiando contraseña:", err);
      alert("Error de conexión al intentar cambiar la contraseña.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h3 style={{ color: '#0f172a', marginBottom: '8px', fontSize: '22px' }}>Cambiar Contraseña</h3>
      <p style={{ color: '#64748b', marginBottom: '25px', fontSize: '14px' }}>
        Ingresa tu usuario (cédula), la contraseña anterior y asigna tu nueva contraseña.
      </p>

      <div style={{ background: '#ffffff', padding: '32px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)', maxWidth: '460px' }}>
        <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>
              Usuario (Número de Cédula):
            </label>
            <input
              type="text"
              placeholder="Ej: admin, consultor o cédula"
              value={usernameInput}
              onChange={(e) => setUsernameInput(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', boxSizing: 'border-box', outline: 'none' }}
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>
              Contraseña Anterior:
            </label>
            <input
              type="password"
              placeholder="Ingresa la contraseña actual"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', boxSizing: 'border-box', outline: 'none' }}
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>
              Nueva Contraseña:
            </label>
            <input
              type="password"
              placeholder="Ingresa la nueva contraseña"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', boxSizing: 'border-box', outline: 'none' }}
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>
              Confirmar Nueva Contraseña:
            </label>
            <input
              type="password"
              placeholder="Vuelve a escribir la nueva contraseña"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1', boxSizing: 'border-box', outline: 'none' }}
              required
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            style={{ padding: '12px', background: '#047857', color: 'white', border: 'none', borderRadius: '6px', fontWeight: '700', cursor: 'pointer', marginTop: '10px', boxShadow: '0 4px 12px rgba(4, 120, 87, 0.2)' }}
          >
            {isSubmitting ? 'Actualizando...' : 'Actualizar Contraseña'}
          </button>
        </form>
      </div>
    </div>
  );
}

// 5. COMPONENTE: ESTADO POR ESTUDIANTE (ESTADÍSTICAS GLOBALES + FILTRO POR ESTADO + CONSULTA INDIVIDUAL)
function StudentStatusView() {
  const [summaryData, setSummaryData] = useState(null);
  const [selectedStatusFilter, setSelectedStatusFilter] = useState('Todos');
  const [listSearchText, setListSearchText] = useState('');
  const [studentsList, setStudentsList] = useState([]);
  const [totalFiltered, setTotalFiltered] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [loadingSummary, setLoadingSummary] = useState(true);

  // Búsqueda individual por cédula
  const [searchCedula, setSearchCedula] = useState('');
  const [resultData, setResultData] = useState(null);
  const [loadingIndividual, setLoadingIndividual] = useState(false);
  const [searchedIndividual, setSearchedIndividual] = useState(false);

  const fetchSummary = useCallback(async (status = 'Todos', search = '', page = 1) => {
    setLoadingSummary(true);
    try {
      const queryParams = new URLSearchParams({
        status_filter: status,
        search: search,
        page: page.toString(),
        limit: '15'
      });
      const response = await fetch(`${API_BASE}/api/admin/student-status-summary?${queryParams}`);
      const data = await response.json();
      setSummaryData(data);
      setStudentsList(data.estudiantes || []);
      setTotalFiltered(data.total_filtrados || 0);
    } catch (err) {
      console.error("Error cargando resumen de estados:", err);
    } finally {
      setLoadingSummary(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary(selectedStatusFilter, listSearchText, currentPage);
  }, [selectedStatusFilter, listSearchText, currentPage, fetchSummary]);

  const handleIndividualSearch = async (e, targetCedula = null) => {
    if (e) e.preventDefault();
    const ced = targetCedula || searchCedula.trim();
    if (!ced) return;
    setLoadingIndividual(true);
    setSearchedIndividual(true);
    try {
      const response = await fetch(`${API_BASE}/api/admin/student-status/${ced}`);
      const data = await response.json();
      setResultData(data);
      setSearchCedula(ced);
      // Scroll suave hacia los resultados de la trayectoria
      window.scrollTo({ top: 380, behavior: 'smooth' });
    } catch (err) {
      console.error("Error buscando estado del estudiante:", err);
      setResultData({ found: false, message: "Error al conectar con el servidor de consulta." });
    } finally {
      setLoadingIndividual(false);
    }
  };

  const spadiesCards = [
    { title: 'Desertor', badgeBg: '#fef2f2', badgeColor: '#b91c1c', border: '#fca5a5', icon: '🔴', desc: 'Estudiante que de manera voluntaria o forzosa no se observa como matriculado por dos o más períodos consecutivos, sin registrar graduación o sin ser retirado por motivos disciplinarios.' },
    { title: 'Activo', badgeBg: '#ecfdf5', badgeColor: '#047857', border: '#a7f3d0', icon: '🟢', desc: 'Estudiante que se encuentra matriculado o que se encontraba matriculado el semestre anterior en un programa académico de pregrado.' },
    { title: 'Graduado', badgeBg: '#eff6ff', badgeColor: '#1d4ed8', border: '#bfdbfe', icon: '🎓', desc: 'Individuo que ha culminado su ciclo académico y ha obtenido un título de nivel de formación.' },
    { title: 'Retirado', badgeBg: '#fffbeb', badgeColor: '#d97706', border: '#fde68a', icon: '⚠️', desc: 'Estudiante que se ausenta de un programa académico de una IES en un período por motivos disciplinarios (no académicos).' }
  ];

  const totalPages = Math.max(1, Math.ceil(totalFiltered / 15));

  return (
    <div>
      <h3 style={{ color: '#0f172a', marginBottom: '8px', fontSize: '22px' }}>Estado por Estudiante (Metodología SPADIES)</h3>
      <p style={{ color: '#64748b', marginBottom: '25px', fontSize: '14px' }}>
        Visualiza las cantidades y porcentajes consolidados por cada estado SPADIES, filtra el listado institucional de estudiantes o consulta la trayectoria individual por cédula.
      </p>

      {/* 📊 BARRA DE ESTADÍSTICAS GLOBALES POR CADA ESTADO (CANTIDADES Y PORCENTAJES) */}
      
      {/* Alerta cuando NO hay archivos cargados en el sistema */}
      {summaryData && summaryData.total_estudiantes === 0 && (
        <div style={{ background: '#fefce8', border: '1px solid #fde047', borderRadius: '10px', padding: '24px 28px', textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>📂</div>
          <h4 style={{ color: '#854d0e', fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>
            Aún no has cargado información de estudiantes en el sistema
          </h4>
          <p style={{ color: '#713f12', fontSize: '13px', maxWidth: '680px', margin: '0 auto 14px auto', lineHeight: '1.6' }}>
            Para comenzar a evaluar y visualizar el estado de los estudiantes y los indicadores, dirígete a la opción <strong>"📂 Cargue de Información"</strong> en el menú lateral y realiza la carga secuencial de tus archivos Excel de matriculados y egresados.
          </p>
          <div style={{ display: 'inline-block', padding: '6px 16px', background: '#ffffff', border: '1px solid #eab308', borderRadius: '6px', fontSize: '12px', color: '#854d0e', fontWeight: '700' }}>
            📌 Sistema listo a la espera del primer cargue de información Excel
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '30px' }}>
        
        {/* Total Estudiantes */}
        <div style={{ background: '#ffffff', padding: '18px 20px', borderRadius: '12px', border: '1px solid #cbd5e1', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', color: '#475569', fontWeight: '700' }}>TOTAL EVALUADOS</span>
            <span style={{ fontSize: '18px' }}>📊</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#0f172a' }}>
            {summaryData ? summaryData.total_estudiantes.toLocaleString() : '—'}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', marginTop: '2px' }}>
            100.00% del total
          </div>
        </div>

        {/* Graduados */}
        <div style={{ background: '#eff6ff', padding: '18px 20px', borderRadius: '12px', border: '1px solid #bfdbfe', boxShadow: '0 4px 12px rgba(29,78,216,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', color: '#1e40af', fontWeight: '700' }}>🎓 GRADUADOS</span>
            <span style={{ fontSize: '18px' }}>🎓</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#1d4ed8' }}>
            {summaryData ? summaryData.resumen.Graduado.cantidad.toLocaleString() : '—'}
          </div>
          <div style={{ fontSize: '12px', color: '#2563eb', fontWeight: '700', marginTop: '2px' }}>
            {summaryData ? summaryData.resumen.Graduado.porcentaje : '—'}
          </div>
        </div>

        {/* Activos */}
        <div style={{ background: '#ecfdf5', padding: '18px 20px', borderRadius: '12px', border: '1px solid #a7f3d0', boxShadow: '0 4px 12px rgba(4,120,87,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', color: '#064e3b', fontWeight: '700' }}>🟢 ACTIVOS</span>
            <span style={{ fontSize: '18px' }}>🟢</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#047857' }}>
            {summaryData ? summaryData.resumen.Activo.cantidad.toLocaleString() : '—'}
          </div>
          <div style={{ fontSize: '12px', color: '#059669', fontWeight: '700', marginTop: '2px' }}>
            {summaryData ? summaryData.resumen.Activo.porcentaje : '—'}
          </div>
        </div>

        {/* Desertores */}
        <div style={{ background: '#fef2f2', padding: '18px 20px', borderRadius: '12px', border: '1px solid #fca5a5', boxShadow: '0 4px 12px rgba(185,28,28,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', color: '#991b1b', fontWeight: '700' }}>🔴 DESERTORES</span>
            <span style={{ fontSize: '18px' }}>🔴</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#b91c1c' }}>
            {summaryData ? summaryData.resumen.Desertor.cantidad.toLocaleString() : '—'}
          </div>
          <div style={{ fontSize: '12px', color: '#dc2626', fontWeight: '700', marginTop: '2px' }}>
            {summaryData ? summaryData.resumen.Desertor.porcentaje : '—'}
          </div>
        </div>

        {/* Retirados */}
        <div style={{ background: '#fffbeb', padding: '18px 20px', borderRadius: '12px', border: '1px solid #fde68a', boxShadow: '0 4px 12px rgba(217,119,6,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', color: '#92400e', fontWeight: '700' }}>⚠️ RETIRADOS</span>
            <span style={{ fontSize: '18px' }}>⚠️</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#d97706' }}>
            {summaryData ? summaryData.resumen.Retirado.cantidad.toLocaleString() : '—'}
          </div>
          <div style={{ fontSize: '12px', color: '#b45309', fontWeight: '700', marginTop: '2px' }}>
            {summaryData ? summaryData.resumen.Retirado.porcentaje : '—'}
          </div>
        </div>

      </div>

      {/* Buscador por Cédula para Consulta Individual */}
      <div style={{ background: '#ffffff', padding: '24px 28px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)', marginBottom: '28px' }}>
        <form onSubmit={handleIndividualSearch} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: 1, minWidth: '280px' }}>
            <label style={{ display: 'block', color: '#475569', fontSize: '13px', marginBottom: '6px', fontWeight: '700' }}>
              🔍 Buscar Trayectoria Individual de un Estudiante por Cédula:
            </label>
            <input
              type="text"
              placeholder="Ingresa número de cédula (ej. 1041329064)"
              value={searchCedula}
              onChange={(e) => setSearchCedula(e.target.value)}
              style={{ width: '100%', padding: '11px 14px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '14px', outline: 'none', background: '#ffffff', color: '#0f172a', boxSizing: 'border-box' }}
              required
            />
          </div>
          <button
            type="submit"
            disabled={loadingIndividual}
            style={{ padding: '11px 22px', background: '#047857', color: 'white', border: 'none', borderRadius: '6px', fontWeight: '700', cursor: 'pointer', fontSize: '14px', marginTop: '20px', boxShadow: '0 4px 12px rgba(4, 120, 87, 0.2)' }}
          >
            {loadingIndividual ? 'Buscando...' : '🔍 Buscar Estudiante'}
          </button>
        </form>
      </div>

      {/* Resultados de la Consulta Individual */}
      {searchedIndividual && (
        <div style={{ marginBottom: '35px' }}>
          {resultData && resultData.found ? (
            <div style={{ background: '#ffffff', padding: '28px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0,0,0,0.03)' }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px', marginBottom: '22px', borderBottom: '1px solid #f1f5f9', pb: '18px' }}>
                <div>
                  <h4 style={{ color: '#0f172a', fontSize: '20px', fontWeight: '700', margin: 0 }}>
                    👤 Cédula: {resultData.cedula}
                  </h4>
                  <p style={{ color: '#047857', fontSize: '14px', fontWeight: '600', margin: '6px 0 0 0' }}>
                    🎓 Programa Académico: {resultData.programa}
                  </p>
                  <p style={{ color: '#64748b', fontSize: '13px', margin: '4px 0 0 0' }}>
                    Periodos matriculados: <strong>{resultData.total_periodos_matriculado}</strong> • Último periodo: <strong>{resultData.ultimo_periodo_registrado}</strong>
                  </p>
                </div>

                <div style={{ background: resultData.meta_spadies.bg_color, border: `1px solid ${resultData.meta_spadies.border_color}`, color: resultData.meta_spadies.badge_color, padding: '12px 22px', borderRadius: '12px', textAlign: 'center' }}>
                  <div style={{ fontSize: '24px' }}>{resultData.meta_spadies.icon}</div>
                  <div style={{ fontSize: '17px', fontWeight: '800' }}>{resultData.meta_spadies.estado}</div>
                  <div style={{ fontSize: '11px', fontWeight: '600', opacity: 0.9 }}>Estado SPADIES</div>
                </div>
              </div>

              <div style={{ background: resultData.meta_spadies.bg_color, border: `1px solid ${resultData.meta_spadies.border_color}`, padding: '18px 22px', borderRadius: '10px', marginBottom: '25px' }}>
                <h5 style={{ color: resultData.meta_spadies.badge_color, fontSize: '14px', fontWeight: '700', margin: '0 0 6px 0' }}>
                  📌 Definición Oficial del Estado en SPADIES: {resultData.meta_spadies.estado}
                </h5>
                <p style={{ color: '#334155', fontSize: '13px', margin: 0, lineHeight: '1.6' }}>
                  • {resultData.meta_spadies.definicion}
                </p>
              </div>

              <h5 style={{ color: '#0f172a', fontSize: '15px', fontWeight: '700', marginBottom: '12px' }}>
                📜 Trayectoria Longitudinal del Estudiante por Semestre:
              </h5>
              <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'center' }}>
                  <thead>
                    <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1', color: '#475569' }}>
                      <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: '700' }}>Periodo Académico</th>
                      <th style={{ padding: '10px 14px', fontWeight: '700' }}>Estado de Matrícula</th>
                      <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: '700' }}>Programa Registrado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {resultData.trayectoria.map((t, idx) => (
                      <tr key={t.periodo} style={{ background: idx % 2 === 0 ? '#ffffff' : '#f9fafb', borderBottom: '1px solid #f1f5f9' }}>
                        <td style={{ padding: '10px 14px', textAlign: 'left', fontWeight: '700', color: '#0f172a' }}>{t.periodo}</td>
                        <td style={{ padding: '10px 14px' }}>
                          <span style={{
                            padding: '4px 10px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: '700',
                            background: t.registrado ? '#ecfdf5' : '#f1f5f9',
                            color: t.registrado ? '#047857' : '#64748b',
                            border: t.registrado ? '1px solid #a7f3d0' : '1px solid #cbd5e1'
                          }}>
                            {t.registrado ? '🟢 Matriculado' : '⚪ No Matriculado'}
                          </span>
                        </td>
                        <td style={{ padding: '10px 14px', textAlign: 'left', color: t.registrado ? '#334155' : '#94a3b8' }}>
                          {t.programa}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>
          ) : (
            <div style={{ background: '#fef2f2', border: '1px solid #fca5a5', color: '#991b1b', padding: '20px 25px', borderRadius: '10px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', marginBottom: '6px' }}>⚠️</div>
              <h4 style={{ margin: '0 0 6px 0', fontSize: '16px', fontWeight: '700' }}>Estudiante No Encontrado</h4>
              <p style={{ margin: 0, fontSize: '13px' }}>{resultData?.message || `No se hallaron registros para la cédula ${searchCedula}`}</p>
            </div>
          )}
        </div>
      )}

      {/* 🎯 BOTONES DE FILTRO INTERACTIVO POR ESTADO Y SECCIÓN DE LISTADO */}
      <div style={{ background: '#ffffff', padding: '24px 28px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)', marginBottom: '30px' }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '15px' }}>
          <div>
            <h4 style={{ color: '#0f172a', fontSize: '17px', fontWeight: '700', margin: 0 }}>
              📋 Directorio e Historial de Estudiantes ({totalFiltered.toLocaleString()})
            </h4>
            <p style={{ color: '#64748b', fontSize: '12px', margin: '4px 0 0 0' }}>
              Filtra por estado o busca por número de cédula o programa académico.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '8px', maxWidth: '300px', width: '100%' }}>
            <input
              type="text"
              placeholder="🔍 Filtrar en listado..."
              value={listSearchText}
              onChange={(e) => { setListSearchText(e.target.value); setCurrentPage(1); }}
              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', outline: 'none', background: '#ffffff', color: '#0f172a' }}
            />
          </div>
        </div>

        {/* Botones de Selección de Filtro por Estado */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '20px' }}>
          {[
            { id: 'Todos', label: 'Todos los Estados', count: summaryData ? summaryData.total_estudiantes : 0, pct: '100%', bg: '#f1f5f9', color: '#334155' },
            { id: 'Graduado', label: '🎓 Graduados', count: summaryData ? summaryData.resumen.Graduado.cantidad : 0, pct: summaryData ? summaryData.resumen.Graduado.porcentaje : '0%', bg: '#eff6ff', color: '#1d4ed8' },
            { id: 'Activo', label: '🟢 Activos', count: summaryData ? summaryData.resumen.Activo.cantidad : 0, pct: summaryData ? summaryData.resumen.Activo.porcentaje : '0%', bg: '#ecfdf5', color: '#047857' },
            { id: 'Desertor', label: '🔴 Desertores', count: summaryData ? summaryData.resumen.Desertor.cantidad : 0, pct: summaryData ? summaryData.resumen.Desertor.porcentaje : '0%', bg: '#fef2f2', color: '#b91c1c' },
            { id: 'Retirado', label: '⚠️ Retirados', count: summaryData ? summaryData.resumen.Retirado.cantidad : 0, pct: summaryData ? summaryData.resumen.Retirado.porcentaje : '0%', bg: '#fffbeb', color: '#d97706' },
          ].map(btn => (
            <button
              key={btn.id}
              onClick={() => { setSelectedStatusFilter(btn.id); setCurrentPage(1); }}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '13px',
                fontWeight: '700',
                cursor: 'pointer',
                border: selectedStatusFilter === btn.id ? `2px solid ${btn.color}` : '1px solid #cbd5e1',
                background: selectedStatusFilter === btn.id ? btn.bg : '#ffffff',
                color: btn.color,
                boxShadow: selectedStatusFilter === btn.id ? `0 2px 8px rgba(0,0,0,0.06)` : 'none',
                transition: 'all 0.2s'
              }}
            >
              {btn.label} ({btn.count.toLocaleString()} • {btn.pct})
            </button>
          ))}
        </div>

        {/* Tabla de Estudiantes Filtrados */}
        <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1', color: '#475569' }}>
                <th style={{ padding: '12px 16px', fontWeight: '700' }}>Cédula / Documento</th>
                <th style={{ padding: '12px 16px', fontWeight: '700' }}>Programa Académico</th>
                <th style={{ padding: '12px 16px', fontWeight: '700', textAlign: 'center' }}>Estado SPADIES</th>
                <th style={{ padding: '12px 16px', fontWeight: '700', textAlign: 'center' }}>Acción</th>
              </tr>
            </thead>
            <tbody>
              {loadingSummary ? (
                <tr>
                  <td colSpan="4" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                    Cargando listado de estudiantes...
                  </td>
                </tr>
              ) : studentsList.length > 0 ? (
                studentsList.map((st, idx) => {
                  let badgeBg = '#ecfdf5', badgeColor = '#047857', badgeIcon = '🟢';
                  if (st.estado === 'Desertor') { badgeBg = '#fef2f2'; badgeColor = '#b91c1c'; badgeIcon = '🔴'; }
                  else if (st.estado === 'Graduado') { badgeBg = '#eff6ff'; badgeColor = '#1d4ed8'; badgeIcon = '🎓'; }
                  else if (st.estado === 'Retirado') { badgeBg = '#fffbeb'; badgeColor = '#d97706'; badgeIcon = '⚠️'; }

                  return (
                    <tr key={st.cedula} style={{ background: idx % 2 === 0 ? '#ffffff' : '#f9fafb', borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '12px 16px', fontWeight: '700', color: '#0f172a' }}>{st.cedula}</td>
                      <td style={{ padding: '12px 16px', color: '#334155' }}>{st.programa}</td>
                      <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                        <span style={{ padding: '5px 12px', borderRadius: '12px', fontSize: '12px', fontWeight: '800', background: badgeBg, color: badgeColor, border: `1px solid ${badgeColor}33` }}>
                          {badgeIcon} {st.estado}
                        </span>
                      </td>
                      <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                        <button
                          onClick={() => handleIndividualSearch(null, st.cedula)}
                          style={{ padding: '6px 12px', background: '#047857', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}
                        >
                          🔎 Ver Trayectoria
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="4" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                    No se encontraron estudiantes para el filtro seleccionado.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Controles de Paginación */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '18px' }}>
          <div style={{ fontSize: '13px', color: '#64748b' }}>
            Página <strong>{currentPage}</strong> de <strong>{totalPages}</strong> ({totalFiltered.toLocaleString()} registros)
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              style={{ padding: '7px 14px', background: currentPage <= 1 ? '#f1f5f9' : '#ffffff', color: currentPage <= 1 ? '#94a3b8' : '#047857', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '13px', fontWeight: '700', cursor: currentPage <= 1 ? 'not-allowed' : 'pointer' }}
            >
              ← Anterior
            </button>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              style={{ padding: '7px 14px', background: currentPage >= totalPages ? '#f1f5f9' : '#ffffff', color: currentPage >= totalPages ? '#94a3b8' : '#047857', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '13px', fontWeight: '700', cursor: currentPage >= totalPages ? 'not-allowed' : 'pointer' }}
            >
              Siguiente →
            </button>
          </div>
        </div>

      </div>

      {/* Referencia Institucional del Manual SPADIES */}
      <h4 style={{ color: '#0f172a', fontSize: '16px', fontWeight: '700', marginBottom: '15px' }}>
        📚 Clasificación Oficial de Estados del Manual SPADIES 3.0:
      </h4>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {spadiesCards.map(c => (
          <div key={c.title} style={{ background: '#ffffff', padding: '20px', borderRadius: '10px', border: `1px solid ${c.border}`, boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <span style={{ fontSize: '18px' }}>{c.icon}</span>
              <span style={{ background: c.badgeBg, color: c.badgeColor, padding: '4px 12px', borderRadius: '12px', fontWeight: '800', fontSize: '13px', border: `1px solid ${c.border}` }}>
                {c.title}
              </span>
            </div>
            <p style={{ color: '#475569', fontSize: '12px', lineHeight: '1.6', margin: 0 }}>
              • {c.desc}
            </p>
          </div>
        ))}
      </div>

    </div>
  );
}

// 6. COMPONENTE: HISTORIAL Y AUDITORÍA DE CAMBIOS (AUDIT TRAIL)
function AuditTrailView() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('TODOS');
  const [entityFilter, setEntityFilter] = useState('TODOS');
  const [loading, setLoading] = useState(false);

  const fetchLogs = useCallback(async (p = 1, q = '', act = 'TODOS', ent = 'TODOS') => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: p.toString(),
        limit: '20'
      });
      if (q.trim()) params.append('search', q.trim());
      if (act !== 'TODOS') params.append('action', act);
      if (ent !== 'TODOS') params.append('entity', ent);

      const res = await fetch(`${API_BASE}/api/admin/audit-logs?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setLogs(data.items || []);
        setTotal(data.total || 0);
        setPage(data.page || 1);
        setTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      console.error("Error cargando auditoría:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLogs(page, search, actionFilter, entityFilter);
  }, [page, actionFilter, entityFilter, fetchLogs]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchLogs(1, search, actionFilter, entityFilter);
  };

  const getActionBadge = (action) => {
    const act = (action || '').toUpperCase();
    const map = {
      'LOGIN_EXITOSO': { bg: '#ecfdf5', color: '#047857', border: '#a7f3d0', icon: '🔓' },
      'LOGIN_FALLIDO': { bg: '#fef2f2', color: '#b91c1c', border: '#fca5a5', icon: '⛔' },
      'CREAR': { bg: '#eff6ff', color: '#1d4ed8', border: '#bfdbfe', icon: '➕' },
      'EDITAR': { bg: '#fffbeb', color: '#d97706', border: '#fde68a', icon: '✏️' },
      'ELIMINAR': { bg: '#fef2f2', color: '#dc2626', border: '#fca5a5', icon: '🗑️' },
      'CARGA_DATOS': { bg: '#f5f3ff', color: '#6d28d9', border: '#ddd6fe', icon: '📂' },
      'PURGA_DATOS': { bg: '#fff1f2', color: '#be123c', border: '#fecdd3', icon: '⚠️' },
      'CAMBIO_CLAVE': { bg: '#f0fdfa', color: '#0f766e', border: '#99f6e4', icon: '🔑' }
    };
    const s = map[act] || { bg: '#f1f5f9', color: '#475569', border: '#cbd5e1', icon: '📌' };
    return (
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '3px 9px', borderRadius: '12px', fontSize: '11px', fontWeight: '700', background: s.bg, color: s.color, border: `1px solid ${s.border}` }}>
        <span>{s.icon}</span> {act}
      </span>
    );
  };

  const formatAuditDetails = (log) => {
    if (!log || !log.details) return '—';

    let data = null;
    if (typeof log.details === 'string' && (log.details.trim().startsWith('{') || log.details.trim().startsWith('['))) {
      try {
        data = JSON.parse(log.details);
      } catch (e) {
        data = null;
      }
    } else if (typeof log.details === 'object') {
      data = log.details;
    }

    if (data && typeof data === 'object') {
      if (log.action === 'CARGA_DATOS' || (data.tipo && (data.archivo || data.archivo_nombre))) {
        const tipo = (data.tipo || 'datos').toUpperCase();
        const per = data.periodo || '';
        const arch = data.archivo || data.archivo_nombre || '';
        const filas = data.filas ? ` (${Number(data.filas).toLocaleString()} registros)` : '';
        return `Cargue de archivo de ${tipo} para el período ${per} desde '${arch}'${filas}.`;
      }
      if (log.action === 'PURGA_DATOS') {
        const tipo = (data.tipo || 'datos').toUpperCase();
        const per = data.periodo || '';
        const arch = data.archivo_nombre || data.archivo || '';
        return `Eliminación física del archivo de ${tipo} del período ${per} ('${arch}'). El período quedó habilitado nuevamente para cargue.`;
      }
      if (log.action === 'CREAR' && (data.cedula || data.role)) {
        return `Creación del usuario ${data.nombre || data.cedula} (Cédula: ${data.cedula}, Rol: ${data.role}). Clave inicial configurada por defecto.`;
      }
      if (log.action === 'EDITAR' && data.old && data.new) {
        const passText = data.password_updated ? ' Se actualizó la contraseña.' : '';
        return `Modificación del usuario ${data.new.nombre || data.new.username} (Rol: ${data.new.role}).${passText}`;
      }
      if (log.action === 'EDITAR' && data.key) {
        return `Actualización del parámetro del sistema '${data.key}': nuevo valor '${data.new_value}' (anterior: '${data.old_value}').`;
      }
      if (log.action === 'ELIMINAR' && data.username) {
        return `Eliminación de la cuenta del usuario ${data.nombre || data.username} (Cédula: ${data.username}).`;
      }
      if (data.motivo) {
        return `Intento fallido de inicio de sesión: ${data.motivo}.`;
      }
      if (data.metodo) {
        return `Inicio de sesión exitoso en la plataforma UCO Analytics (${data.metodo}).`;
      }
    }

    return log.details;
  };

  return (
    <div>
      <h3 style={{ color: '#0f172a', marginBottom: '8px', fontSize: '22px' }}>Historial y Auditoría de Cambios (Audit Trail)</h3>
      <p style={{ color: '#64748b', marginBottom: '25px', fontSize: '14px' }}>
        Registro inmutable y cronológico de todas las operaciones realizadas en el sistema (creación de usuarios, cargas de archivos, autenticaciones y modificaciones).
      </p>

      {/* Barra de Filtros y Búsqueda */}
      <div style={{ background: '#ffffff', padding: '18px 22px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)', marginBottom: '20px', display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
        
        <form onSubmit={handleSearchSubmit} style={{ flex: '1 1 260px', display: 'flex', gap: '8px' }}>
          <input
            type="text"
            placeholder="🔍 Buscar por cédula, nombre o detalle..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ flex: 1, padding: '9px 12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', outline: 'none', background: '#ffffff', color: '#0f172a' }}
          />
          <button type="submit" style={{ padding: '9px 15px', background: '#047857', color: 'white', border: 'none', borderRadius: '6px', fontSize: '13px', fontWeight: '700', cursor: 'pointer' }}>
            Buscar
          </button>
        </form>

        <div style={{ flex: '0 1 180px' }}>
          <label style={{ display: 'block', fontSize: '11px', color: '#64748b', fontWeight: '700', marginBottom: '4px' }}>FILTRAR POR ACCIÓN:</label>
          <select
            value={actionFilter}
            onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
            style={{ width: '100%', padding: '9px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', outline: 'none', background: '#ffffff', color: '#0f172a' }}
          >
            <option value="TODOS">Todas las Acciones</option>
            <option value="LOGIN_EXITOSO">Inicio Sesión Exitoso</option>
            <option value="LOGIN_FALLIDO">Inicio Sesión Fallido</option>
            <option value="CREAR">Crear Registro</option>
            <option value="EDITAR">Editar Registro</option>
            <option value="ELIMINAR">Eliminar Registro</option>
            <option value="CARGA_DATOS">Carga de Datos</option>
            <option value="PURGA_DATOS">Purga de Datos</option>
            <option value="CAMBIO_CLAVE">Cambio de Clave</option>
          </select>
        </div>

        <div style={{ flex: '0 1 160px' }}>
          <label style={{ display: 'block', fontSize: '11px', color: '#64748b', fontWeight: '700', marginBottom: '4px' }}>FILTRAR POR ENTIDAD:</label>
          <select
            value={entityFilter}
            onChange={(e) => { setEntityFilter(e.target.value); setPage(1); }}
            style={{ width: '100%', padding: '9px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', outline: 'none', background: '#ffffff', color: '#0f172a' }}
          >
            <option value="TODOS">Todas las Entidades</option>
            <option value="USUARIO">Usuarios</option>
            <option value="ARCHIVO_DATOS">Archivos de Datos</option>
            <option value="PARAMETRO">Parámetros</option>
          </select>
        </div>

      </div>

      {/* Tabla de Registros de Auditoría */}
      <div style={{ overflowX: 'auto', background: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.03)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ background: '#ecfdf5', textAlign: 'left', borderBottom: '2px solid #047857' }}>
              <th style={{ padding: '12px 14px', color: '#064e3b', fontWeight: '700' }}>Fecha y Hora</th>
              <th style={{ padding: '12px 14px', color: '#064e3b', fontWeight: '700' }}>Usuario (Cédula)</th>
              <th style={{ padding: '12px 14px', color: '#064e3b', fontWeight: '700' }}>Rol</th>
              <th style={{ padding: '12px 14px', color: '#064e3b', fontWeight: '700' }}>Acción Realizada</th>
              <th style={{ padding: '12px 14px', color: '#064e3b', fontWeight: '700' }}>Entidad / ID</th>
              <th style={{ padding: '12px 14px', color: '#064e3b', fontWeight: '700' }}>Dirección IP</th>
              <th style={{ padding: '12px 14px', color: '#064e3b', fontWeight: '700' }}>Detalles de la Operación</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="7" style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>Cargando eventos de auditoría...</td></tr>
            ) : logs.length === 0 ? (
              <tr><td colSpan="7" style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>No se encontraron registros de auditoría con los criterios seleccionados.</td></tr>
            ) : (
              logs.map(log => (
                <tr key={log.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                  <td style={{ padding: '11px 14px', color: '#475569', whiteSpace: 'nowrap', fontWeight: '600' }}>{log.timestamp}</td>
                  <td style={{ padding: '11px 14px', color: '#0f172a', fontWeight: '700' }}>
                    {log.user_name}
                    <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 'normal' }}>{log.username}</div>
                  </td>
                  <td style={{ padding: '11px 14px' }}>
                    <span style={{ textTransform: 'capitalize', padding: '2px 8px', borderRadius: '8px', fontSize: '11px', background: '#f1f5f9', color: '#334155', fontWeight: '600' }}>
                      {log.user_role}
                    </span>
                  </td>
                  <td style={{ padding: '11px 14px' }}>
                    {getActionBadge(log.action)}
                  </td>
                  <td style={{ padding: '11px 14px', color: '#047857', fontWeight: '600' }}>
                    {log.entity} {log.entity_id ? `(${log.entity_id})` : ''}
                  </td>
                  <td style={{ padding: '11px 14px', color: '#64748b', fontFamily: 'monospace', fontSize: '12px' }}>
                    {log.ip_address}
                  </td>
                  <td style={{ padding: '11px 14px', color: '#1e293b', maxWidth: '340px', wordBreak: 'break-word', fontSize: '12px', lineHeight: '1.45' }}>
                    {formatAuditDetails(log)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Paginador */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ fontSize: '13px', color: '#64748b' }}>
          Total registros: <strong>{total}</strong> • Página <strong>{page}</strong> de <strong>{totalPages}</strong>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            disabled={page <= 1}
            onClick={() => setPage(p => Math.max(1, p - 1))}
            style={{ padding: '6px 14px', background: page <= 1 ? '#f1f5f9' : '#ffffff', color: page <= 1 ? '#94a3b8' : '#047857', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '12px', fontWeight: '700', cursor: page <= 1 ? 'not-allowed' : 'pointer' }}
          >
            ← Anterior
          </button>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            style={{ padding: '6px 14px', background: page >= totalPages ? '#f1f5f9' : '#ffffff', color: page >= totalPages ? '#94a3b8' : '#047857', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '12px', fontWeight: '700', cursor: page >= totalPages ? 'not-allowed' : 'pointer' }}
          >
            Siguiente →
          </button>
        </div>
      </div>
    </div>
  );
}

// 7. COMPONENTE: CATÁLOGO DE PARÁMETROS DEL SISTEMA
function SystemParametersView() {
  const [params, setParams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingKey, setEditingKey] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [savingKey, setSavingKey] = useState(null);

  const fetchParams = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/admin/parameters`);
      if (res.ok) {
        const data = await res.json();
        setParams(data);
      }
    } catch (err) {
      console.error("Error cargando parámetros:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchParams();
  }, []);

  const startEdit = (param) => {
    setEditingKey(param.key);
    setEditValue(param.value);
  };

  const handleSave = async (key) => {
    setSavingKey(key);
    try {
      const res = await fetch(`${API_BASE}/api/admin/parameters/${key}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: editValue })
      });
      const data = await res.json();
      if (res.ok) {
        alert("✅ Parámetro actualizado exitosamente.");
        setEditingKey(null);
        fetchParams();
      } else {
        alert(data.error?.message || data.detail || "Error al actualizar parámetro.");
      }
    } catch (err) {
      alert("Error de conexión al guardar el parámetro.");
    } finally {
      setSavingKey(null);
    }
  };

  // Agrupar parámetros por categoría
  const grouped = params.reduce((acc, p) => {
    const cat = p.category || 'GENERAL';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(p);
    return acc;
  }, {});

  return (
    <div>
      <h3 style={{ color: '#0f172a', marginBottom: '8px', fontSize: '22px' }}>Catálogo de Parámetros del Sistema</h3>
      <p style={{ color: '#64748b', marginBottom: '25px', fontSize: '14px' }}>
        Administra las reglas de negocio institucionales (criterios de deserción SPADIES, políticas de seguridad y límites del sistema) sin necesidad de compilar ni reiniciar.
      </p>

      {loading ? (
        <div style={{ background: '#ffffff', padding: '30px', borderRadius: '10px', textAlign: 'center', color: '#64748b' }}>
          Cargando catálogo de parámetros...
        </div>
      ) : (
        Object.keys(grouped).map(category => (
          <div key={category} style={{ marginBottom: '30px' }}>
            <h4 style={{ color: '#047857', fontSize: '16px', fontWeight: '700', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              📁 Categoría: {category} ({grouped[category].length} parámetros)
            </h4>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '16px' }}>
              {grouped[category].map(param => (
                <div key={param.key} style={{ background: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '20px', boxShadow: '0 4px 12px rgba(0,0,0,0.02)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                      <span style={{ fontFamily: 'monospace', fontWeight: '700', color: '#0f172a', fontSize: '13px' }}>
                        {param.key}
                      </span>
                      <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '6px', background: '#ecfdf5', color: '#047857', fontWeight: '700', border: '1px solid #a7f3d0' }}>
                        {param.data_type}
                      </span>
                    </div>

                    <p style={{ color: '#64748b', fontSize: '13px', lineHeight: '1.5', margin: '0 0 16px 0' }}>
                      {param.description}
                    </p>
                  </div>

                  <div style={{ background: '#f8fafc', padding: '12px 14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    {editingKey === param.key ? (
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <input
                          type="text"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          style={{ flex: 1, padding: '7px 10px', borderRadius: '6px', border: '1px solid #047857', background: '#ffffff', color: '#0f172a', fontSize: '13px', outline: 'none' }}
                        />
                        <button
                          disabled={savingKey === param.key}
                          onClick={() => handleSave(param.key)}
                          style={{ padding: '7px 12px', background: '#047857', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}
                        >
                          {savingKey === param.key ? '...' : 'Guardar'}
                        </button>
                        <button
                          onClick={() => setEditingKey(null)}
                          style={{ padding: '7px 10px', background: '#64748b', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', cursor: 'pointer' }}
                        >
                          ✕
                        </button>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontSize: '11px', color: '#94a3b8', fontWeight: '600' }}>VALOR CONFIGURADO:</div>
                          <div style={{ fontSize: '15px', fontWeight: '800', color: '#0f172a' }}>
                            {param.value}
                          </div>
                        </div>

                        {param.is_editable ? (
                          <button
                            onClick={() => startEdit(param)}
                            style={{ padding: '6px 12px', background: '#0284c7', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', fontWeight: '600', cursor: 'pointer' }}
                          >
                            ✏️ Modificar
                          </button>
                        ) : (
                          <span style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic' }}>
                            Protegido
                          </span>
                        )}
                      </div>
                    )}

                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '11px', color: '#94a3b8' }}>
                      <span>Por defecto: {param.default_value}</span>
                      <span>Modificado por: {param.updated_by}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

// 8. COMPONENTE PRINCIPAL CON MENÚ LATERAL Y MÓVIL RESPONSIVE
function App() {
  const [usernameInput, setUsernameInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [role, setRole] = useState(localStorage.getItem("userRole"));
  const [username, setUsername] = useState(localStorage.getItem("username"));
  const [userNombre, setUserNombre] = useState(localStorage.getItem("userNombre") || '');

  const [activeTab, setActiveTab] = useState(role === 'consultor' ? 'indicadores' : 'usuarios');
  const [showLoginChangePassword, setShowLoginChangePassword] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameInput, password: passwordInput })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("userRole", data.role);
        localStorage.setItem("username", data.username);
        localStorage.setItem("userNombre", data.nombre || data.username);
        if (data.token) {
          localStorage.setItem("authToken", data.token);
        }
        setRole(data.role);
        setUsername(data.username);
        setUserNombre(data.nombre || data.username);
        setActiveTab(data.role === 'consultor' ? 'indicadores' : 'usuarios');
      } else {
        alert("Usuario o contraseña incorrectos");
      }
    } catch (err) {
      console.error("Error en login:", err);
      alert("No se pudo conectar con el servidor.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("userRole");
    localStorage.removeItem("username");
    localStorage.removeItem("userNombre");
    localStorage.removeItem("authToken");
    setRole(null);
    setUsername(null);
    setUserNombre('');
    setMobileMenuOpen(false);
  };

  if (!role) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: 'linear-gradient(135deg, #f8fafc 0%, #ecfdf5 50%, #f1f5f9 100%)', fontFamily: 'Segoe UI, sans-serif', padding: '20px' }}>
        <div style={{ background: '#ffffff', padding: '42px 38px', borderRadius: '16px', boxShadow: '0 15px 35px rgba(0,0,0,0.06)', width: '100%', maxWidth: '440px', border: '1px solid #e2e8f0' }}>
          
          <img src="/logo-uco.svg" alt="Universidad Católica de Oriente" style={{ height: '80px', display: 'block', margin: '0 auto 15px auto' }} />

          <div style={{ background: '#fefce8', border: '1px solid #fde047', color: '#854d0e', fontSize: '12px', fontWeight: '700', padding: '7px 14px', borderRadius: '20px', textAlign: 'center', marginBottom: '25px' }}>
            ⭐ Sistema de Analítica de Deserción UCO
          </div>

          {showLoginChangePassword ? (
            <div>
              <ChangePasswordView onSuccessBack={() => setShowLoginChangePassword(false)} />
              <button
                onClick={() => setShowLoginChangePassword(false)}
                style={{ width: '100%', marginTop: '15px', padding: '10px', background: 'transparent', color: '#047857', border: '1px solid #047857', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '600' }}
              >
                ← Volver al Inicio de Sesión
              </button>
            </div>
          ) : (
            <>
              <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
                <div>
                  <label style={{ display: 'block', color: '#475569', fontSize: '12px', marginBottom: '6px', fontWeight: '600' }}>Usuario (Cédula o Cuenta):</label>
                  <input
                    type="text"
                    placeholder="Ej: admin, consultor o número de cédula"
                    value={usernameInput}
                    onChange={(e) => setUsernameInput(e.target.value)}
                    style={{ width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #cbd5e1', background: '#ffffff', color: '#0f172a', fontSize: '14px', outline: 'none', boxSizing: 'border-box' }}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#475569', fontSize: '12px', marginBottom: '6px', fontWeight: '600' }}>Contraseña:</label>
                  <input
                    type="password"
                    placeholder="Contraseña de acceso"
                    value={passwordInput}
                    onChange={(e) => setPasswordInput(e.target.value)}
                    style={{ width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #cbd5e1', background: '#ffffff', color: '#0f172a', fontSize: '14px', outline: 'none', boxSizing: 'border-box' }}
                    required
                  />
                </div>
                <button type="submit" style={{ padding: '12px', background: '#047857', color: '#ffffff', border: '1px solid #eab308', borderRadius: '6px', fontSize: '15px', fontWeight: '700', cursor: 'pointer', boxShadow: '0 4px 12px rgba(4, 120, 87, 0.25)', marginTop: '5px' }}>
                  Iniciar Sesión
                </button>
              </form>

              <div style={{ marginTop: '22px', textAlign: 'center' }}>
                <button
                  onClick={() => setShowLoginChangePassword(true)}
                  style={{ background: 'none', border: 'none', color: '#047857', fontSize: '13px', cursor: 'pointer', textDecoration: 'underline', fontWeight: '600' }}
                >
                  🔑 ¿Deseas cambiar tu contraseña?
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  }

  const getButtonStyle = (tabName) => ({
    width: '100%',
    textAlign: 'left',
    padding: '12px 16px',
    background: activeTab === tabName ? '#047857' : 'transparent',
    color: activeTab === tabName ? '#ffffff' : '#334155',
    border: 'none',
    borderLeft: activeTab === tabName ? '4px solid #eab308' : '4px solid transparent',
    borderRadius: '0 8px 8px 0',
    cursor: 'pointer',
    fontWeight: activeTab === tabName ? '700' : '600',
    fontSize: '14px',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  });

  const selectTab = (tabName) => {
    setActiveTab(tabName);
    setMobileMenuOpen(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#f8fafc', fontFamily: 'Segoe UI, sans-serif', overflow: 'hidden' }}>

      {/* Barra Superior Móvil (Smartphones & Tablets) */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 20px', background: '#ffffff', borderBottom: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,0.03)', zIndex: 1000 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '38px', height: '38px', background: '#ecfdf5', color: '#047857', border: '1px solid #a7f3d0', borderRadius: '8px', cursor: 'pointer', fontSize: '18px', fontWeight: '700' }}
            title="Menú de Navegación"
          >
            {mobileMenuOpen ? '✕' : '☰'}
          </button>
          <img src="/logo-uco.svg" alt="UCO Logo" style={{ height: '32px', width: 'auto' }} />
          <span style={{ fontWeight: '700', fontSize: '15px', color: '#0f172a' }}>
            Analítica de Deserción UCO
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ textAlign: 'right', display: 'none' }} className="desktop-user-badge">
            <span style={{ fontSize: '13px', fontWeight: '700', color: '#064e3b' }}>{userNombre || username}</span>
          </div>
          <button
            onClick={handleLogout}
            style={{ padding: '7px 12px', background: '#fef2f2', color: '#dc2626', border: '1px solid #fca5a5', borderRadius: '6px', cursor: 'pointer', fontWeight: '700', fontSize: '12px' }}
          >
            Salir
          </button>
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', position: 'relative' }}>

        {/* Backdrop para cerrar menú en móviles */}
        {mobileMenuOpen && (
          <div
            onClick={() => setMobileMenuOpen(false)}
            style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.45)', zIndex: 900 }}
          />
        )}

        {/* Menú Lateral (Drawer responsive) */}
        <aside style={{
          width: '280px',
          background: '#ffffff',
          borderRight: '1px solid #e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '24px 20px',
          boxShadow: '2px 0 10px rgba(0,0,0,0.02)',
          zIndex: 950,
          position: mobileMenuOpen ? 'fixed' : 'relative',
          top: mobileMenuOpen ? '63px' : 'auto',
          bottom: mobileMenuOpen ? '0' : 'auto',
          left: mobileMenuOpen ? '0' : 'auto',
          height: mobileMenuOpen ? 'calc(100vh - 63px)' : '100%',
          transform: mobileMenuOpen ? 'translateX(0)' : undefined
        }}>
          <div>
            <div style={{ background: '#ecfdf5', padding: '14px 16px', borderRadius: '10px', border: '1px solid #a7f3d0', textAlign: 'center', marginBottom: '24px' }}>
              <div style={{ color: '#064e3b', fontWeight: '700', fontSize: '14px', marginBottom: '3px' }}>
                👤 {userNombre || username}
              </div>
              <div style={{ fontSize: '12px', color: '#047857' }}>
                Cédula: <strong>{username}</strong> • <span style={{ textTransform: 'capitalize', color: '#854d0e', fontWeight: '700', background: '#fefce8', padding: '2px 8px', borderRadius: '10px', border: '1px solid #fde047' }}>{role}</span>
              </div>
            </div>

            <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {role === 'administrador' && (
                <>
                  <button onClick={() => selectTab('usuarios')} style={getButtonStyle('usuarios')}>
                    ⚙️ Config. de Usuarios
                  </button>
                  <button onClick={() => selectTab('cargue')} style={getButtonStyle('cargue')}>
                    📂 Cargue de Información
                  </button>
                  <button onClick={() => selectTab('auditoria')} style={getButtonStyle('auditoria')}>
                    📜 Historial de Auditoría
                  </button>
                  <button onClick={() => selectTab('parametros')} style={getButtonStyle('parametros')}>
                    🛠️ Parámetros del Sistema
                  </button>
                </>
              )}

              <button onClick={() => selectTab('indicadores')} style={getButtonStyle('indicadores')}>
                📊 Indicadores y Estadísticas
              </button>

              <button onClick={() => selectTab('estado-estudiante')} style={getButtonStyle('estado-estudiante')}>
                👤 Estado por Estudiante
              </button>

              <button onClick={() => selectTab('cambiar-clave')} style={getButtonStyle('cambiar-clave')}>
                🔑 Cambiar Contraseña
              </button>
            </nav>
          </div>

          <button
            onClick={handleLogout}
            style={{ width: '100%', padding: '11px', background: '#fef2f2', color: '#dc2626', border: '1px solid #fca5a5', borderRadius: '8px', cursor: 'pointer', fontWeight: '700', fontSize: '13px' }}
          >
            Cerrar Sesión
          </button>
        </aside>

        {/* Contenido Principal */}
        <main style={{ flex: 1, padding: '28px', overflowY: 'auto', background: '#f8fafc' }}>
          {activeTab === 'usuarios' && role === 'administrador' && <UserManagement />}
          {activeTab === 'cargue' && role === 'administrador' && <UploadView />}
          {activeTab === 'auditoria' && role === 'administrador' && <AuditTrailView />}
          {activeTab === 'parametros' && role === 'administrador' && <SystemParametersView />}
          {activeTab === 'indicadores' && <IndicatorsView />}
          {activeTab === 'estado-estudiante' && <StudentStatusView />}
          {activeTab === 'cambiar-clave' && <ChangePasswordView initialUsername={username} />}
        </main>

      </div>

    </div>
  );
}

export default App;