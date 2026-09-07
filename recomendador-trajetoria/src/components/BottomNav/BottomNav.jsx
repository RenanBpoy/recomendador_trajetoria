import { CircleUserRound, Grid3X3, House, ListChecks } from 'lucide-react'
// import { CalendarDays } from 'lucide-react' // Agenda temporariamente oculta da navegação.
import { NavLink } from 'react-router-dom'
import {
  useFirstAccessGuideAction,
  useFirstAccessGuideTarget,
} from '../FirstAccessGuide/FirstAccessGuideContext'
import './BottomNav.css'

const items = [
  { id: 'início', label: 'Início', to: '/home', icon: House },
  { id: 'grade', label: 'Grade', to: '/grade', icon: Grid3X3 },
  { id: 'plano', label: 'Plano', to: '/semana', icon: ListChecks },
  // { id: 'agenda', label: 'Agenda', to: '/calendario', icon: CalendarDays },
  { id: 'perfil', label: 'Perfil', to: '/perfil', icon: CircleUserRound },
]

function BottomNav({ active }) {
  const homeGuideRef = useFirstAccessGuideTarget('first-access-home-nav')
  const completeGuideAction = useFirstAccessGuideAction()

  return (
    <nav className="bottom-nav" aria-label="Navegação principal">
      {items.map(({ id, label, to, icon: Icon }) => (
        <NavLink
          key={id}
          ref={id === 'início' ? homeGuideRef : undefined}
          to={to}
          onClick={() => {
            if (id === 'início') completeGuideAction('return-home-after-history')
          }}
          className={({ isActive }) => {
            const selected = active ? active === id : isActive
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
