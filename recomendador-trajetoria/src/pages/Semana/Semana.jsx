import { RotateCw, Save } from 'lucide-react'
import { useEffect, useState } from 'react'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import CargaPlanejada from '../../components/CargaPlanejada/CargaPlanejada'
import PlanItemDialog from '../../components/PlanItemDialog/PlanItemDialog'
import ScheduleGrid from '../../components/ScheduleGrid/ScheduleGrid'
import { getWeeklyPlan, saveWeeklyPlan } from '../../services/plan'
import { weeklyActivityLabel } from '../../utils/weeklyPlan'
import './Semana.css'

const activityTypes = [
  { value: 'DISCIPLINA', label: '+ Disciplina' },
  { value: 'ESTAGIO', label: '+ Estágio' },
  { value: 'OUTRO', label: '+ Outro' },
]

function viewItems(items) {
  return items.map((item) => ({
    ...item,
    _key: `saved-${item.id}`,
    hora_inicio: String(item.hora_inicio).slice(0, 5),
    hora_fim: String(item.hora_fim).slice(0, 5),
    observacoes: item.observacoes || '',
  }))
}

function minutes(value) {
  const [hour, minute] = String(value).split(':').map(Number)
  return hour * 60 + minute
}

function overlaps(first, second) {
  return first.dia_semana === second.dia_semana
    && minutes(first.hora_inicio) < minutes(second.hora_fim)
    && minutes(second.hora_inicio) < minutes(first.hora_fim)
}

function durationByType(items, type) {
  const totalMinutes = items
    .filter((item) => item.tipo_atividade === type)
    .reduce((total, item) => total + minutes(item.hora_fim) - minutes(item.hora_inicio), 0)
  return totalMinutes / 60
}

function Semana() {
  const [selectedType, setSelectedType] = useState('DISCIPLINA')
  const [savedItems, setSavedItems] = useState([])
  const [items, setItems] = useState([])
  const [editorItem, setEditorItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [dirty, setDirty] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    getWeeklyPlan()
      .then((loaded) => {
        if (!active) return
        const normalized = viewItems(loaded)
        setSavedItems(normalized)
        setItems(normalized)
      })
      .catch((requestError) => {
        if (active) setError(requestError.message || 'Não foi possível carregar o plano salvo.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => { active = false }
  }, [])

  function openNewItem(day, hour) {
    const start = `${String(hour).padStart(2, '0')}:00`
    const end = `${String(Math.min(22, hour + 2)).padStart(2, '0')}:00`
    setError('')
    setEditorItem({
      _key: `new-${Date.now()}-${day}-${hour}`,
      tipo_atividade: selectedType,
      titulo: weeklyActivityLabel(selectedType),
      dia_semana: day,
      hora_inicio: start,
      hora_fim: end,
      observacoes: '',
    })
  }

  function applyItem(item) {
    const nextItem = String(item._key).startsWith('new-')
      ? { ...item, _key: `draft-${Date.now()}-${Math.random().toString(36).slice(2)}` }
      : item
    const conflict = items.find((current) => current._key !== nextItem._key && overlaps(current, nextItem))
    if (conflict) {
      setError(`Esse horário se sobrepõe a “${weeklyActivityLabel(conflict.tipo_atividade)}”.`)
      return false
    }
    setItems((current) => {
      const exists = current.some((entry) => entry._key === nextItem._key)
      return exists
        ? current.map((entry) => (entry._key === nextItem._key ? nextItem : entry))
        : [...current, nextItem]
    })
    setDirty(true)
    setFeedback('Alteração aplicada. Use “Salvar plano” para persistir.')
    setError('')
    return true
  }

  function removeItem(key) {
    setItems((current) => current.filter((item) => item._key !== key))
    setDirty(true)
    setFeedback('Atividade removida do rascunho. Salve o plano para confirmar.')
    setError('')
  }

  function restoreSavedPlan() {
    setItems(savedItems)
    setEditorItem(null)
    setDirty(false)
    setError('')
    setFeedback('Última versão salva restaurada.')
  }

  async function persistPlan() {
    setSaving(true)
    setError('')
    setFeedback('')
    try {
      const payload = items.map(({ tipo_atividade, dia_semana, hora_inicio, hora_fim, observacoes }) => ({
        tipo_atividade,
        titulo: weeklyActivityLabel(tipo_atividade),
        dia_semana,
        hora_inicio,
        hora_fim,
        observacoes: observacoes || null,
      }))
      const saved = viewItems(await saveWeeklyPlan(payload))
      setSavedItems(saved)
      setItems(saved)
      setDirty(false)
      setFeedback('Plano semanal salvo com sucesso.')
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível salvar o plano semanal.')
    } finally {
      setSaving(false)
    }
  }

  const disciplineHours = durationByType(items, 'DISCIPLINA')
  const internshipHours = durationByType(items, 'ESTAGIO')
  const otherHours = durationByType(items, 'OUTRO')

  return (
    <main className="mobile-page week-page">
      <AppHeader title="Monte sua semana" icon={RotateCw} onClick={restoreSavedPlan} ariaLabel="Restaurar plano salvo" />
      <div className="week-page__content">
        <div className="schedule-filters">
          {activityTypes.map((type) => (
            <button key={type.value} className={selectedType === type.value ? 'is-active' : ''} type="button" onClick={() => setSelectedType(type.value)}>{type.label}</button>
          ))}
        </div>

        {loading ? <p className="week-page__loading">Carregando plano...</p> : (
          <ScheduleGrid entries={items} onSelectSlot={openNewItem} onSelectEntry={setEditorItem} />
        )}

        <CargaPlanejada
          horasDisciplinas={disciplineHours}
          horasEstagio={internshipHours}
          horasOutras={otherHours}
        />

        {feedback && <p className="week-page__feedback is-success" role="status">{feedback}</p>}
        {error && <p className="week-page__feedback is-error" role="alert">{error}</p>}

        <button className="primary-button week-page__save" type="button" disabled={!dirty || saving || loading} onClick={persistPlan}>
          <Save size={15} />{saving ? 'Salvando...' : 'Salvar plano'}
        </button>
      </div>
      <BottomNav active="plano" />
      {editorItem && (
        <PlanItemDialog
          key={editorItem._key}
          item={editorItem}
          onClose={() => setEditorItem(null)}
          onSave={applyItem}
          onDelete={removeItem}
        />
      )}
    </main>
  )
}

export default Semana
