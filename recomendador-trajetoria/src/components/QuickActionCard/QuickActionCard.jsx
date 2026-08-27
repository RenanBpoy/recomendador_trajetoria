import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import './QuickActionCard.css'

function QuickActionCard({ to, icon: Icon, tone = 'cyan', title, description }) {
  return (
    <Link className="home-action-card" to={to}>
      <span className={`home-action-card__icon home-action-card__icon--${tone}`}>
        <Icon aria-hidden="true" />
      </span>
      <span className="home-action-card__text">
        <strong>{title}</strong>
        <small>{description}</small>
      </span>
      <ArrowRight className="home-action-card__arrow" aria-hidden="true" />
    </Link>
  )
}

export default QuickActionCard
