import { useMemo, useState } from 'react'
import { weeklyActivityLabel } from '../../utils/weeklyPlan'
import ProfileDialog from '../ProfileDialog/ProfileDialog'
import './PlanItemDialog.css'

const days = [
  { value: 1, label: 'Segunda-feira' },
  { value: 2, label: 'Terça-feira' },
  { value: 3, label: 'Quarta-feira' },
  { value: 4, label: 'Quinta-feira' },
  { value: 5, label: 'Sexta-feira' },
]

const times = Array.from({ length: 8 }, (_, index) => `${String(8 + index * 2).padStart(2, '0')}:00`)

function PlanItemDialog({ item, onClose, onSave, onDelete }) {
  const [form, setForm] = useState(item)
  const [submitError, setSubmitError] = useState('')
  const endTimes = useMemo(
    () => times.filter((time) => time > form.hora_inicio),
    [form.hora_inicio],
  )

  function change(field, value) {
    setSubmitError('')
    setForm((current) => {
      const updated = { ...current, [field]: value }
      if (field === 'hora_inicio' && updated.hora_fim <= value) {
        updated.hora_fim = times.find((time) => time > value) || '22:00'
      }
      return updated
    })
  }

  function submit(event) {
    event.preventDefault()
    const saved = onSave({
      ...form,
      titulo: weeklyActivityLabel(form.tipo_atividade),
      observacoes: form.observacoes.trim() || null,
    })
    if (saved === false) {
      setSubmitError('Já existe outra atividade nesse período. Escolha outro dia ou horário.')
      return
    }
    onClose()
  }

  const editing = !String(item._key).startsWith('new-')

  return (
    <ProfileDialog
      title={editing ? 'Editar atividade' : 'Adicionar atividade'}
      subtitle="Escolha o tipo de atividade, o dia e o período."
      onClose={onClose}
    >
      <form className="plan-item-form" onSubmit={submit}>
        <label>
          <span>Tipo</span>
          <select value={form.tipo_atividade} onChange={(event) => change('tipo_atividade', event.target.value)}>
            <option value="DISCIPLINA">Disciplina</option>
            <option value="ESTAGIO">Estágio</option>
            <option value="OUTRO">Outra atividade</option>
          </select>
        </label>
        <label>
          <span>Dia</span>
          <select value={form.dia_semana} onChange={(event) => change('dia_semana', Number(event.target.value))}>
            {days.map((day) => <option key={day.value} value={day.value}>{day.label}</option>)}
          </select>
        </label>
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
          <textarea value={form.observacoes || ''} maxLength={500} rows={3} placeholder="Turma, local ou algum lembrete" onChange={(event) => change('observacoes', event.target.value)} />
        </label>
        {submitError && <p className="plan-item-form__error" role="alert">{submitError}</p>}
        <div className="plan-item-form__actions">
          {editing && <button className="danger-button" type="button" onClick={() => { onDelete(item._key); onClose() }}>Remover</button>}
          <button className="profile-dialog__submit" type="submit">{editing ? 'Aplicar alteração' : 'Adicionar ao plano'}</button>
        </div>
      </form>
    </ProfileDialog>
  )
}

export default PlanItemDialog
