import { createContext, useCallback, useContext, useEffect, useState } from 'react';

// ---------------------------------------------------------------
// Notificaciones (reemplazan los alert() del navegador)
// ---------------------------------------------------------------
const ToastContext = createContext(() => {});

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const notify = useCallback((message, type = 'info', timeout = 6000) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, message, type }]);
    if (timeout) setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), timeout);
  }, []);
  const close = (id) => setToasts((t) => t.filter((x) => x.id !== id));
  return (
    <ToastContext.Provider value={notify}>
      {children}
      <div className="toasts" role="status" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            <span style={{ whiteSpace: 'pre-line' }}>{t.message}</span>
            <button className="toast-close" onClick={() => close(t.id)} aria-label="Cerrar">×</button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);

// ---------------------------------------------------------------
// Bloques de interfaz
// ---------------------------------------------------------------
export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="page-header">
      <div>
        <h2>{title}</h2>
        {subtitle && <p className="muted">{subtitle}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </div>
  );
}

export function Card({ title, children, actions, className = '' }) {
  return (
    <section className={`card ${className}`}>
      {(title || actions) && (
        <div className="card-head">
          {title && <h3>{title}</h3>}
          {actions && <div className="card-actions">{actions}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

export function Alert({ type = 'info', title, children }) {
  return (
    <div className={`alert alert-${type}`}>
      {title && <strong>{title} </strong>}
      {children}
    </div>
  );
}

export function Empty({ children }) {
  return <div className="empty">{children}</div>;
}

export function Spinner({ label = 'Cargando…' }) {
  return <div className="spinner"><span className="spinner-dot" />{label}</div>;
}

export function Badge({ tone = 'neutral', children }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

export function Field({ label, children, hint }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}

// Campo de contraseña con botón (ojo) para mostrar u ocultar lo escrito. Es opcional: por defecto va oculto.
export function PasswordInput({ value, onChange, autoComplete, required, ...rest }) {
  const [visible, setVisible] = useState(false);
  const label = visible ? 'Ocultar contraseña' : 'Mostrar contraseña';
  return (
    <span className="pw-wrap">
      <input
        {...rest}
        type={visible ? 'text' : 'password'}
        autoComplete={autoComplete}
        value={value}
        onChange={onChange}
        required={required}
      />
      <button type="button" className="pw-toggle" onClick={() => setVisible((v) => !v)}
        aria-label={label} title={label} aria-pressed={visible}>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"
          strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" />
          <circle cx="12" cy="12" r="3" />
          {visible && <path d="M3 3l18 18" />}
        </svg>
      </button>
    </span>
  );
}

export function Segmented({ options, value, onChange, ariaLabel }) {
  return (
    <div className="segmented" role="radiogroup" aria-label={ariaLabel}>
      {options.map((o) => (
        <button
          key={o.id}
          type="button"
          role="radio"
          aria-checked={value === o.id}
          className={value === o.id ? 'active' : ''}
          onClick={() => onChange(o.id)}
          title={o.help || ''}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Pagination({ page, totalPages, onChange, total }) {
  return (
    <div className="pagination">
      <span className="muted">
        Página <strong>{page}</strong> de <strong>{totalPages}</strong>
        {total !== undefined && <> · {Number(total).toLocaleString('es-CO')} registros</>}
      </span>
      <div className="btn-row">
        <button className="btn btn-light" disabled={page <= 1} onClick={() => onChange(page - 1)}>← Anterior</button>
        <button className="btn btn-light" disabled={page >= totalPages} onClick={() => onChange(page + 1)}>Siguiente →</button>
      </div>
    </div>
  );
}

export function Modal({ title, children, onClose, footer, wide = false }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose?.();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);
  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose?.()}>
      <div className={`modal ${wide ? 'modal-wide' : ''}`} role="dialog" aria-modal="true" aria-label={title}>
        <div className="modal-head">
          <h3>{title}</h3>
          {onClose && <button className="icon-btn" onClick={onClose} aria-label="Cerrar">×</button>}
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-foot">{footer}</div>}
      </div>
    </div>
  );
}

// Muestra una contraseña temporal una sola vez, con botón para copiar.
export function TempPasswordNotice({ username, password, onClose }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try { await navigator.clipboard.writeText(password); setCopied(true); } catch { setCopied(false); }
  };
  return (
    <Modal title="Contraseña temporal" onClose={onClose}
      footer={<button className="btn btn-primary" onClick={onClose}>Entendido</button>}>
      <p>Entregue esta contraseña al usuario <strong>{username}</strong> por un canal seguro. No se volverá a mostrar.</p>
      <div className="temp-pass">
        <code>{password}</code>
        <button className="btn btn-light" onClick={copy}>{copied ? 'Copiada ✓' : 'Copiar'}</button>
      </div>
      <p className="muted small">Al ingresar por primera vez, el sistema le pedirá definir su propia contraseña.</p>
    </Modal>
  );
}
