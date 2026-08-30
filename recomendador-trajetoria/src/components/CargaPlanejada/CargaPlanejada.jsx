import './CargaPlanejada.css'

const categories = [
  { key: 'disciplinas', label: 'em disciplinas', tone: 'mint' },
  { key: 'estagio', label: 'de estágio', tone: 'purple' },
  { key: 'outras', label: 'em outras atividades', tone: 'pink' },
]

function formatHours(value) {
  return Number(value || 0).toLocaleString('pt-BR', {
    minimumFractionDigits: Number.isInteger(value) ? 0 : 1,
    maximumFractionDigits: 1,
  })
}

function classifyLoad(totalHours, weeklyLimit) {
  if (totalHours === 0) {
    return {
      title: 'Semana livre',
      message: 'Adicione atividades ao seu plano',
    }
  }

  const occupancy = totalHours / weeklyLimit
  if (occupancy <= 0.6) {
    return { title: 'Semana leve', message: 'Boa margem na semana' }
  }
  if (occupancy <= 0.8) {
    return { title: 'Semana moderada', message: 'Carga dentro do esperado' }
  }
  return { title: 'Semana intensa', message: 'Pouca margem disponível' }
}

function CargaPlanejada({
  horasDisciplinas = 0,
  horasEstagio = 0,
  horasOutras = 0,
  limiteSemanal = 40,
}) {
  const hours = {
    disciplinas: horasDisciplinas,
    estagio: horasEstagio,
    outras: horasOutras,
  }
  const totalHours = Object.values(hours).reduce((total, value) => total + value, 0)
  const safeLimit = Math.max(1, limiteSemanal)
  const barReference = Math.max(safeLimit, totalHours)
  const classification = classifyLoad(totalHours, safeLimit)

  return (
    <section className="carga-planejada" aria-labelledby="carga-planejada-titulo">
      <div className="carga-planejada__cabecalho">
        <div>
          <p className="carga-planejada__label">Carga planejada</p>
          <h2 id="carga-planejada-titulo" className="carga-planejada__titulo">
            {classification.title}
          </h2>
        </div>

        <div className="carga-planejada__total">
          <strong>{formatHours(totalHours)} h</strong>
          <span>no total</span>
        </div>
      </div>

      <div
        className="carga-planejada__barra"
        role="img"
        aria-label={`${formatHours(horasDisciplinas)} horas em disciplinas, ${formatHours(horasEstagio)} horas de estágio e ${formatHours(horasOutras)} horas em outras atividades`}
      >
        {categories.map((category) => (
          <span
            key={category.key}
            className={`carga-planejada__segmento carga-planejada__segmento--${category.tone}`}
            style={{ width: `${(hours[category.key] / barReference) * 100}%` }}
          />
        ))}
      </div>

      <div className="carga-planejada__rodape">
        <div className="carga-planejada__legendas">
          {categories.map((category) => (
            <span key={category.key}>
              <i className={`carga-planejada__indicador carga-planejada__indicador--${category.tone}`} />
              <strong>{formatHours(hours[category.key])} h</strong>
              {category.label}
            </span>
          ))}
        </div>

        <p className="carga-planejada__mensagem">{classification.message}</p>
      </div>
    </section>
  )
}

export default CargaPlanejada
