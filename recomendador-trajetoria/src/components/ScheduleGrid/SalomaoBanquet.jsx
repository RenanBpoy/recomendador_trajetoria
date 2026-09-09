import { UtensilsCrossed } from 'lucide-react'

export default function SalomaoBanquet({ row }) {
  return (
    <div
      className="weekly-calendar__banquet"
      style={{ gridColumn: '2 / -1', gridRow: row }}
      role="note"
      aria-label="Banquete do Salomão, de segunda a sexta, das 12h30 às 13h30. Marcação visual, não bloqueia atividades."
    >
      <UtensilsCrossed size={12} aria-hidden="true" />
      <span>Banquete do Salomão <small>12h30–13h30</small></span>
    </div>
  )
}
