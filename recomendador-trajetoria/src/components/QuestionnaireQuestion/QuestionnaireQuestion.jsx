import './QuestionnaireQuestion.css'

function QuestionnaireQuestion({ number, children }) {
  return (
    <article className="questionnaire-question">
      <span className="questionnaire-question__number" aria-hidden="true">
        {String(number).padStart(2, '0')}
      </span>
      <div className="questionnaire-question__content">
        <span>AFIRMAÇÃO</span>
        <h2>{children}</h2>
      </div>
    </article>
  )
}

export default QuestionnaireQuestion
