import { ArrowLeft } from 'lucide-react'
import AppHeader from '../AppHeader/AppHeader'
import BottomNav from '../BottomNav/BottomNav'
import '../../pages/Professores/Professores.css'
import './ConsultaAcademica.css'

export default function ConsultaLayout({ title, back = '/home', children }) {
  return <main className="mobile-page consulta-page"><AppHeader title={title} icon={ArrowLeft} to={back} ariaLabel="Voltar" /><div className="professors-content">{children}</div><BottomNav /></main>
}

export function ConsultaEstado({ error, retry }) {
  return error ? <div role="alert"><p>{error}</p><button className="outline-button" onClick={retry}>Tentar novamente</button></div> : <p role="status">Carregando informações...</p>
}
