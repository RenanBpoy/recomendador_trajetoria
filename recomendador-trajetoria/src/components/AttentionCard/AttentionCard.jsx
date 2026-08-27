import { ArrowRight, TriangleAlert } from 'lucide-react'
import { Link } from 'react-router-dom'
import './AttentionCard.css'

function AttentionCard({ title, to = '/horario-disponivel' }) {
  return (
    <Link className="home-attention" to={to}>
      <span className="home-attention__icon"><TriangleAlert aria-hidden="true" /></span>
      <span className="home-attention__text">
        <small>PONTO DE ATENÇÃO</small>
        <strong>{title}</strong>
      </span>
      <ArrowRight className="home-attention__arrow" aria-hidden="true" />
    </Link>
  )
}

export default AttentionCard
