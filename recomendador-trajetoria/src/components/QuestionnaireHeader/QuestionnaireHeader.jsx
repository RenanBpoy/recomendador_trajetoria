import { ArrowLeft, X } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import './QuestionnaireHeader.css'

function QuestionnaireHeader() {
  const navigate = useNavigate()

  return (
    <header className="questionnaire-header">
      <button
        className="icon-square questionnaire-header__action"
        type="button"
        aria-label="Voltar"
        onClick={() => navigate(-1)}
      >
        <ArrowLeft size={18} />
      </button>

      <div className="questionnaire-header__title">
        <strong>Questionário</strong>
        <span>Perfil acadêmico</span>
      </div>

      <Link
        className="icon-square questionnaire-header__action"
        to="/home"
        aria-label="Fechar questionário"
      >
        <X size={18} />
      </Link>
    </header>
  )
}

export default QuestionnaireHeader
