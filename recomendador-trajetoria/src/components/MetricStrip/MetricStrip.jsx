import './MetricStrip.css'

function MetricStrip({ title, items }) {
  return (
    <section className="metric-strip">
      <h2>{title}</h2>
      <div className="metric-strip__grid">
        {items.map(({ value, label, tone = 'cyan' }) => (
          <article key={label} className={`metric-strip__item metric-strip__item--${tone}`}>
            <strong>{value}</strong>
            <span>{label}</span>
          </article>
        ))}
      </div>
    </section>
  )
}

export default MetricStrip
