import { CalendarDays, CircleUserRound, Grid3X3, House, ListChecks } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import './BottomNav.css'

const mainItems = [
  { label: 'Início', to: '/home', icon: House },
  { label: 'Grade', to: '/grade', icon: Grid3X3 },
  { label: 'Agenda', to: '/calendario', icon: CalendarDays },
]

function BottomNav({ active, lastItem = 'perfil' }) {
  const finalItem = lastItem === 'plano'
    ? { label: 'Plano', to: '/semana', icon: ListChecks }
    : { label: 'Perfil', to: '/perfil', icon: CircleUserRound }

  return (
    <nav className="bottom-nav" aria-label="Navegação principal">
      {[...mainItems, finalItem].map(({ label, to, icon: Icon }) => (
        <NavLink
          key={label}
          to={to}
          className={({ isActive }) => {
            const selected = active ? active === label.toLowerCase() : isActive
            return `bottom-nav__item${selected ? ' is-active' : ''}`
          }}
        >
          <Icon size={16} strokeWidth={2} />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  )
}

export default BottomNav
