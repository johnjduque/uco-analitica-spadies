import { useEffect, useState } from 'react';
import './App.css';
import { api, onUnauthorized, session } from './api/client';
import { Card, PageHeader, ToastProvider } from './components/ui';
import AuditView from './views/AuditView';
import ChangePasswordView from './views/ChangePasswordView';
import IndicatorsView from './views/IndicatorsView';
import LoadsView from './views/LoadsView';
import LoginView from './views/LoginView';
import ParametersView from './views/ParametersView';
import ProgramsView from './views/ProgramsView';
import StudentsView from './views/StudentsView';
import UsersView from './views/UsersView';

const NAV = [
  { id: 'indicadores', label: 'Indicadores', icon: '📊', roles: ['administrador', 'consultor'] },
  { id: 'estudiantes', label: 'Estado por estudiante', icon: '👤', roles: ['administrador', 'consultor'] },
  { id: 'cargas', label: 'Carga de información', icon: '📂', roles: ['administrador'] },
  { id: 'programas', label: 'Catálogo de programas', icon: '🎓', roles: ['administrador'] },
  { id: 'usuarios', label: 'Usuarios', icon: '⚙️', roles: ['administrador'] },
  { id: 'auditoria', label: 'Auditoría', icon: '📜', roles: ['administrador'] },
  { id: 'parametros', label: 'Parámetros', icon: '🛠️', roles: ['administrador'] },
  { id: 'clave', label: 'Cambiar contraseña', icon: '🔑', roles: ['administrador', 'consultor'] },
];

function readHash() {
  return window.location.hash.replace('#/', '') || 'indicadores';
}

function Shell() {
  const [user, setUser] = useState(session.user);
  const [tab, setTab] = useState(readHash);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    onUnauthorized(() => setUser(null));
    const onHash = () => setTab(readHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  // Verifica que la sesión guardada siga siendo válida (rol y estado vigentes).
  useEffect(() => {
    if (!session.token) return;
    api.get('/auth/me')
      .then((me) => { session.save(session.token, me); setUser(me); })
      .catch(() => {});
  }, []);

  const logout = () => {
    session.clear();
    setUser(null);
  };

  const handleAuth = (res) => {
    session.save(res.token, res.user);
    setUser(res.user);
  };

  if (!user || !session.token) return <LoginView onLogin={handleAuth} />;

  if (user.must_change_password) {
    return (
      <div className="login-page">
        <div className="login-card wide">
          <img src="/logo-uco.svg" alt="UCO" className="login-logo" />
          <h2 className="center">Defina su contraseña</h2>
          <p className="muted center">Hola, {user.nombre}.</p>
          <ChangePasswordView forced onChanged={handleAuth} />
          <button className="btn btn-link" onClick={logout}>Salir</button>
        </div>
      </div>
    );
  }

  const items = NAV.filter((n) => n.roles.includes(user.role));
  const current = items.find((n) => n.id === tab) ? tab : 'indicadores';
  const go = (id) => { window.location.hash = `#/${id}`; setTab(id); setMenuOpen(false); };

  return (
    <div className="app">
      <header className="topbar">
        <button className="icon-btn menu-btn" onClick={() => setMenuOpen(!menuOpen)} aria-label="Menú">{menuOpen ? '✕' : '☰'}</button>
        <img src="/logo-uco.svg" alt="UCO" className="topbar-logo" />
        <span className="topbar-title">Analítica de Deserción UCO</span>
        <span className="topbar-user">{user.nombre} · <em>{user.role}</em></span>
        <button className="btn btn-light btn-sm" onClick={logout}>Salir</button>
      </header>
      <div className="layout">
        {menuOpen && <div className="backdrop" onClick={() => setMenuOpen(false)} />}
        <nav className={`sidebar ${menuOpen ? 'open' : ''}`} aria-label="Navegación principal">
          {items.map((n) => (
            <button key={n.id} className={`nav-item ${current === n.id ? 'active' : ''}`} onClick={() => go(n.id)}>
              <span aria-hidden="true">{n.icon}</span> {n.label}
            </button>
          ))}
        </nav>
        <main className="content">
          {current === 'indicadores' && <IndicatorsView />}
          {current === 'estudiantes' && <StudentsView />}
          {current === 'cargas' && <LoadsView />}
          {current === 'programas' && <ProgramsView />}
          {current === 'usuarios' && <UsersView currentUser={user} />}
          {current === 'auditoria' && <AuditView />}
          {current === 'parametros' && <ParametersView />}
          {current === 'clave' && (
            <>
              <PageHeader title="Cambiar contraseña" />
              <Card><ChangePasswordView onChanged={handleAuth} /></Card>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <Shell />
    </ToastProvider>
  );
}
