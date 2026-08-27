import { Layers3 } from 'lucide-react'
import './QuestionnaireSection.css'

function QuestionnaireSection({
  sectionNumber,
  totalSections,
  title,
  description,
  currentStep,
  totalSteps,
}) {
  return (
    <section className="questionnaire-section" aria-labelledby="questionnaire-section-title">
      <div className="questionnaire-section__main">
        <span className="questionnaire-section__icon" aria-hidden="true">
          <Layers3 size={23} />
        </span>
        <div>
          <span className="questionnaire-section__eyebrow">SEÇÃO {sectionNumber} DE {totalSections}</span>
          <h1 id="questionnaire-section-title">{title}</h1>
          <p>{description}</p>
        </div>
      </div>

      <div className="questionnaire-section__steps" aria-label={`Pergunta ${currentStep} de ${totalSteps} desta seção`}>
        {Array.from({ length: totalSteps }, (_, index) => {
          const step = index + 1
          const state = step < currentStep ? 'done' : step === currentStep ? 'current' : 'pending'
          return <span className={`questionnaire-section__step questionnaire-section__step--${state}`} key={step} />
        })}
      </div>
    </section>
  )
}

export default QuestionnaireSection
