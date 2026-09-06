import { useId, useMemo, useState } from 'react'
import { weeklyActivityLabel } from '../../utils/weeklyPlan'
import DisciplinePlanPicker from '../DisciplinePlanPicker/DisciplinePlanPicker'
import ProfileDialog from '../ProfileDialog/ProfileDialog'
import './PlanItemDialog.css'

const days = [
  { value: 1, label: 'Segunda-feira' },
  { value: 2, label: 'Terça-feira' },
  { value: 3, label: 'Quarta-feira' },
  { value: 4, label: 'Quinta-feira' },
  { value: 5, label: 'Sexta-feira' },
]

const times = Array.from({ length: 29 }, (_, index) => {
  const totalMinutes = 8 * 60 + index * 30
  const hour = Math.floor(totalMinutes / 60)
  const minute = totalMinutes % 60
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
})

function defaultEndTime(start) {
  const [hour, minute] = start.split(':').map(Number)
  const totalMinutes = Math.min(22 * 60, hour * 60 + minute + 120)
  return `${String(Math.floor(totalMinutes / 60)).padStart(2, '0')}:${String(totalMinutes % 60).padStart(2, '0')}`
}

function minutes(value) {
  const [hour, minute] = String(value).split(':').map(Number)
  return hour * 60 + minute
}

function offeringMatchesItem(offering, item) {
  return offering.disciplina_nome === item.titulo && offering.horarios.some((schedule) => (
    schedule.dia_semana === item.dia_semana
    && minutes(schedule.hora_inicio) < minutes(item.hora_fim)
    && minutes(item.hora_inicio) < minutes(schedule.hora_fim)
  ))
}

function PlanItemDialog({
  item,
  disciplines = [],
  disciplinesLoading = false,
  disciplinesError = '',
  planItems = [],
  onClose,
  onSave,
  onDelete,
}) {
  const [form, setForm] = useState(item)
  const [submitError, setSubmitError] = useState('')
  const formId = useId()
  const isDiscipline = form.tipo_atividade === 'DISCIPLINA'
  const selectedDay = days.find((day) => day.value === form.dia_semana)?.label
  const endTimes = useMemo(
    () => times.filter((time) => time > form.hora_inicio),
    [form.hora_inicio],
  )

  const selectedOffering = disciplines.find(
    (offering) => offering.id === form.oferta_turma_id,
  ) || disciplines.find((offering) => offeringMatchesItem(offering, form)) || null

  function change(field, value) {
    setSubmitError('')
    setForm((current) => {
      const updated = { ...current, [field]: value }
      if (field === 'hora_inicio' && updated.hora_fim <= value) {
        updated.hora_fim = defaultEndTime(value)
      }
      return updated
    })
  }

  function submit(event) {
    event.preventDefault()
    if (form.tipo_atividade === 'DISCIPLINA' && !selectedOffering) {
      setSubmitError('Selecione uma disciplina antes de adicionar ao plano.')
      return
    }
    const entries = form.tipo_atividade === 'DISCIPLINA'
      ? selectedOffering.horarios.map((schedule) => ({
        ...form,
        oferta_turma_id: selectedOffering.id,
        disciplina_codigo: selectedOffering.disciplina_codigo,
        codigo: selectedOffering.disciplina_codigo,
        grupo_disciplina: `oferta:${selectedOffering.id}`,
        titulo: selectedOffering.disciplina_nome,
        dia_semana: schedule.dia_semana,
        hora_inicio: String(schedule.hora_inicio).slice(0, 5),
        hora_fim: String(schedule.hora_fim).slice(0, 5),
        observacoes: [
          selectedOffering.disciplina_codigo,
          `Turma ${selectedOffering.codigo_turma}`,
          schedule.sala,
        ].filter(Boolean).join(' · '),
      }))
      : [{
        ...form,
        titulo: weeklyActivityLabel(form.tipo_atividade),
        observacoes: form.observacoes.trim() || null,
      }]
    const saved = onSave(entries, editing ? item._key : null)
    if (saved === false) {
      setSubmitError('Já existe outra atividade nesse período. Ajuste o horário ou selecione outro dia na grade.')
      return
    }
    onClose()
  }

  const editing = !String(item._key).startsWith('new-')
  const actions = (
    <div className="plan-item-form__actions">
      {editing && <button className="danger-button" type="button" onClick={() => { onDelete(item._key); onClose() }}>Remover</button>}
      <button className="profile-dialog__submit" type="submit" form={formId}>{editing ? 'Aplicar alteração' : 'Adicionar ao plano'}</button>
    </div>
  )

  return (
    <ProfileDialog
      title={editing ? 'Editar atividade' : 'Adicionar atividade'}
      subtitle={isDiscipline ? 'Escolha a disciplina para o seu plano.' : [weeklyActivityLabel(form.tipo_atividade), selectedDay].filter(Boolean).join(' · ')}
      onClose={onClose}
      className="plan-item-dialog"
      footer={actions}
    >
      <form id={formId} className="plan-item-form" onSubmit={submit}>
        {form.tipo_atividade === 'DISCIPLINA' && (
          <DisciplinePlanPicker
            disciplines={disciplines}
            selectedOfferingId={selectedOffering?.id || ''}
            loading={disciplinesLoading}
            error={disciplinesError}
            planItems={planItems}
            editingItem={item}
            onSelect={(offering) => setForm((current) => ({
              ...current,
              oferta_turma_id: offering.id,
              disciplina_codigo: offering.disciplina_codigo,
              titulo: offering.disciplina_nome,
            }))}
          />
        )}
        {form.tipo_atividade !== 'DISCIPLINA' && (
          <>
            <div className="plan-item-form__times">
              <label>
                <span>Início</span>
                <select value={form.hora_inicio} onChange={(event) => change('hora_inicio', event.target.value)}>
                  {times.slice(0, -1).map((time) => <option key={time} value={time}>{time}</option>)}
                </select>
              </label>
              <label>
                <span>Fim</span>
                <select value={form.hora_fim} onChange={(event) => change('hora_fim', event.target.value)}>
                  {endTimes.map((time) => <option key={time} value={time}>{time}</option>)}
                </select>
              </label>
            </div>
            <label>
              <span>Observação opcional</span>
              <textarea value={form.observacoes || ''} maxLength={500} rows={3} placeholder="Local ou algum lembrete" onChange={(event) => change('observacoes', event.target.value)} />
            </label>
          </>
        )}
        {submitError && <p className="plan-item-form__error" role="alert">{submitError}</p>}
      </form>
    </ProfileDialog>
  )
}

export default PlanItemDialog
