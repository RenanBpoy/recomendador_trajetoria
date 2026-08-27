import './AgreementScale.css'

const answerLabels = {
  1: 'Discordo totalmente',
  2: 'Discordo muito',
  3: 'Discordo',
  4: 'Discordo parcialmente',
  5: 'Neutro',
  6: 'Concordo parcialmente',
  7: 'Concordo',
  8: 'Concordo',
  9: 'Concordo muito',
  10: 'Concordo totalmente',
}

function AgreementScale({ selectedValue = null, onChange, disabled = false }) {
  const selectedLabel = selectedValue
    ? `${selectedValue} · ${answerLabels[selectedValue]}`
    : 'Selecione uma resposta'

  return (
    <section className="agreement-scale" aria-labelledby="agreement-scale-title">
      <div className="agreement-scale__heading">
        <h2 id="agreement-scale-title">Quanto esta afirmação representa você?</h2>
        <strong>{selectedLabel}</strong>
      </div>

      <div className="agreement-scale__options" aria-label="Escala de concordância de 1 a 10" aria-disabled={disabled}>
        {Array.from({ length: 10 }, (_, index) => {
          const value = index + 1
          return (
            <button
              className={value === selectedValue ? 'agreement-scale__option agreement-scale__option--selected' : 'agreement-scale__option'}
              type="button"
              disabled={disabled}
              onClick={() => onChange?.(value)}
              aria-label={`${value}: ${answerLabels[value]}`}
              aria-pressed={value === selectedValue}
              key={value}
            >
              {value}
            </button>
          )
        })}
      </div>

      <div className="agreement-scale__extremes" aria-hidden="true">
        <span>Discordo totalmente</span>
        <span>Concordo totalmente</span>
      </div>
    </section>
  )
}

export default AgreementScale
