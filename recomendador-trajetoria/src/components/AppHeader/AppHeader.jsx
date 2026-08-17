import { Link } from 'react-router-dom'
import './AppHeader.css'

function AppHeader({ title, icon: Icon, to, onClick, ariaLabel = 'Abrir ação' }) {
  const action = Icon ? (
    to ? (
      <Link className="icon-square" to={to} aria-label={ariaLabel}>
        <Icon size={18} strokeWidth={2} />
      </Link>
    ) : (
      <button className="icon-square" type="button" onClick={onClick} aria-label={ariaLabel}>
        <Icon size={18} strokeWidth={2} />
      </button>
    )
  ) : null

  return (
    <header className="app-header">
      <div className="app-header__copy">
        <span className="app-header__brand">TCC</span>
        {title && <h1 className="app-header__title">{title}</h1>}
      </div>
      {action}
    </header>
  )
}

export default AppHeader
