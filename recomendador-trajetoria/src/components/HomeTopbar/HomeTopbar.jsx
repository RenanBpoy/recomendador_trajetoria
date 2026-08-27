import { Link } from 'react-router-dom'
import './HomeTopbar.css'

function profileInitial(name) {
  return String(name || 'Estudante').trim().charAt(0).toLocaleUpperCase('pt-BR')
}

function HomeTopbar({ studentName }) {
  return (
    <header className="home-topbar">
      <div className="home-topbar__brand">
        <strong>TCC</strong>
        <span>Painel acadêmico</span>
      </div>
      <Link className="home-topbar__avatar" to="/perfil" aria-label="Abrir perfil">
        {profileInitial(studentName)}
      </Link>
    </header>
  )
}

export default HomeTopbar
