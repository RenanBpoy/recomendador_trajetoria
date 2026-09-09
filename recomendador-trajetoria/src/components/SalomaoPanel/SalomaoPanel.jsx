import { BookOpen, NotebookTabs, CircleUserRound, ListChecks, MoonStar, UsersRound } from 'lucide-react'
import { Link } from 'react-router-dom'
import BalaoMascote from '../BalaoMascote/BalaoMascote'
import { hasGeneratedRecommendation } from '../../services/recommendation'
import './SalomaoPanel.css'

export default function SalomaoPanel({ target, open, onClose, userId }) {
  const recommendationAvailable = hasGeneratedRecommendation(userId)

  return (
    <BalaoMascote target={target} open={open} onClose={onClose} showCloseButton={false} text="O que você gostaria de explorar? Meus bigodes apontam o caminho!" dialogLabel="Atalhos do Salomão" className="salomao-panel" focusOnOpen>
      <div className="salomao-panel__shortcuts">
        <button className="salomao-shortcut--theme" type="button" disabled title="Mudar tema — em breve" aria-label="Mudar tema, em breve">
          <MoonStar size={24} aria-hidden="true" /><span>Tema</span><small>Em breve</small>
        </button>
        <Link className="salomao-shortcut--teachers" to="/professores" onClick={onClose}>
          <UsersRound size={24} aria-hidden="true" /><span>Professores</span><small>Conheça as turmas</small>
        </Link>
        <Link className="salomao-shortcut--disciplines" to="/disciplinas" onClick={onClose}>
          <BookOpen size={24} aria-hidden="true" /><span>Disciplinas</span><small>Dados e aprovação</small>
        </Link>
        <Link className="salomao-shortcut--diaries" to="/diarios-classe" onClick={onClose}>
          <NotebookTabs size={24} aria-hidden="true" /><span>Diários de classe</span><small>Consulte uma turma</small>
        </Link>
        <Link className="salomao-shortcut--profile" to="/perfil" onClick={onClose}>
          <CircleUserRound size={24} aria-hidden="true" /><span>Perfil</span><small>Sua conta</small>
        </Link>
        {recommendationAvailable ? (
          <Link className="salomao-shortcut--analyzed" to="/tambem-analisamos" onClick={onClose}>
            <ListChecks size={24} aria-hidden="true" /><span>Também analisamos</span><small>Veja o que ficou de fora</small>
          </Link>
        ) : (
          <button className="salomao-shortcut--analyzed" type="button" disabled title="Disponível após sua primeira recomendação" aria-label="Também analisamos, disponível após sua primeira recomendação">
            <ListChecks size={24} aria-hidden="true" /><span>Também analisamos</span><small>Após a recomendação</small>
          </button>
        )}
      </div>
    </BalaoMascote>
  )
}
