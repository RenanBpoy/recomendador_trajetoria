import './DailyEvent.css'

function DailyEvent({ time, title, detail, tone = 'blue' }) {
  return (
    <article className={`daily-event daily-event--${tone}`}>
      <time>{time}</time>
      <div>
        <strong>{title}</strong>
        <span>{detail}</span>
      </div>
    </article>
  )
}

export default DailyEvent
