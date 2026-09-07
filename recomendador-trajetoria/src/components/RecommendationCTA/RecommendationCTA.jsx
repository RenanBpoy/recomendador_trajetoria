import { ArrowRight, LockKeyhole, Sparkles } from 'lucide-react'
import { useFirstAccessGuideAction } from '../FirstAccessGuide/FirstAccessGuideContext'
import './RecommendationCTA.css'

function RecommendationCTA({ enabled = false, checking = false, onStart, guideRef }) {
  const completeGuideAction = useFirstAccessGuideAction()
  const buttonLabel = checking ? 'Verificando etapas' : enabled ? 'Começar análise' : 'Complete as etapas'

  function handleStart() {
    completeGuideAction('start-recommendation')
    onStart?.()
  }

  return (
    <section className={`recommendation-cta${enabled ? ' is-enabled' : ' is-locked'}`}>
      <div className="recommendation-cta__orbit" aria-hidden="true">
        <span className="recommendation-cta__dot recommendation-cta__dot--top" />
        <span className="recommendation-cta__dot recommendation-cta__dot--bottom" />

        <div className="recommendation-cta__icon">
          {enabled ? <Sparkles size={20} strokeWidth={2.2} /> : <LockKeyhole size={18} strokeWidth={2.2} />}
        </div>
      </div>

      <div className="recommendation-cta__content">
        <h3>Montar plano</h3>
        <p>{enabled ? 'Baseado nas suas preferências' : 'Conclua as três etapas para liberar.'}</p>
      </div>

      <button
        ref={guideRef}
        className="recommendation-cta__button"
        type="button"
        onClick={handleStart}
        disabled={!enabled || checking}
      >
        <span>{buttonLabel}</span>
        {enabled && <ArrowRight size={16} strokeWidth={2.4} />}
      </button>
    </section>
  )
}

export default RecommendationCTA
