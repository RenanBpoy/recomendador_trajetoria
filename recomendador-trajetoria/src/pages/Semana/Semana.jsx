import { RotateCw, Save } from 'lucide-react'
import { useEffect, useState } from 'react'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import CargaPlanejada from '../../components/CargaPlanejada/CargaPlanejada'
import {
  useFirstAccessGuideAction,
  useFirstAccessGuideTarget,
} from '../../components/FirstAccessGuide/FirstAccessGuideContext'
import PlanItemDialog from '../../components/PlanItemDialog/PlanItemDialog'
import ScheduleGrid from '../../components/ScheduleGrid/ScheduleGrid'
import { listNotApprovedDisciplines } from '../../services/academic'
import { getStoredAuth } from '../../services/auth'
import { getWeeklyPlan, saveWeeklyPlan } from '../../services/plan'
import { getRecommendationContext } from '../../services/recommendation'
import { weeklyActivityLabel, weeklyDisciplineIdentity } from '../../utils/weeklyPlan'
import './Semana.css'

const activityTypes = [
  { value: 'DISCIPLINA', label: '+ Disciplina', tone: 'mint' },
  { value: 'ESTAGIO', label: '+ Estágio', tone: 'purple' },
  { value: 'OUTRO', label: '+ Outro', tone: 'pink' },
]

function viewItems(items) {
  return items.map((item) => {
    const identity = weeklyDisciplineIdentity(item)
    return {
      ...item,
      _key: `saved-${item.id}`,
      codigo: identity.codigo,
      grupo_disciplina: identity.grupo,
      hora_inicio: String(item.hora_inicio).slice(0, 5),
      hora_fim: String(item.hora_fim).slice(0, 5),
      observacoes: item.observacoes || '',
    }
  })
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

function samePlanSlot(first, second) {
  return first.tipo_atividade === second.tipo_atividade
    && first.titulo === second.titulo
    && first.dia_semana === second.dia_semana
    && String(first.hora_inicio).slice(0, 5) === String(second.hora_inicio).slice(0, 5)
    && String(first.hora_fim).slice(0, 5) === String(second.hora_fim).slice(0, 5)
}

function durationByType(items, type) {
  const totalMinutes = items
    .filter((item) => item.tipo_atividade === type)
    .reduce((total, item) => total + minutes(item.hora_fim) - minutes(item.hora_inicio), 0)
  return totalMinutes / 60
}

function Semana() {
  const planGridGuideRef = useFirstAccessGuideTarget('first-access-plan-grid')
  const planSaveGuideRef = useFirstAccessGuideTarget('first-access-plan-save')
  const completeGuideAction = useFirstAccessGuideAction()
  const registration = getStoredAuth()?.perfil?.matricula
  const [selectedType, setSelectedType] = useState('DISCIPLINA')
  const [savedItems, setSavedItems] = useState([])
  const [items, setItems] = useState([])
  const [editorItem, setEditorItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [dirty, setDirty] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [error, setError] = useState('')
  const [disciplines, setDisciplines] = useState([])
  const [disciplinesLoading, setDisciplinesLoading] = useState(false)
  const [disciplinesError, setDisciplinesError] = useState('')
  const [targetPeriod, setTargetPeriod] = useState(null)

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

  async function loadDisciplineOptions(item) {
    setDisciplines([])
    setDisciplinesError('')
    setDisciplinesLoading(true)
    if (!registration) {
      setDisciplinesError('Não foi possível identificar a matrícula do usuário.')
      setDisciplinesLoading(false)
      return
    }
    try {
      let period = targetPeriod
      if (!period) {
        const context = await getRecommendationContext()
        period = { ano: context.ano_alvo, semestre: context.semestre_alvo }
        setTargetPeriod(period)
      }
      const available = await listNotApprovedDisciplines(registration, {
        ...period,
        diaSemana: item.dia_semana,
        horaInicio: item.hora_inicio,
        horaFim: item.hora_fim,
      })
      setDisciplines(available)
    } catch (requestError) {
      setDisciplinesError(
        requestError.message || 'Não foi possível carregar as disciplinas desse horário.',
      )
    } finally {
      setDisciplinesLoading(false)
    }
  }

  function openNewItem(day, hour) {
    const start = `${String(Math.floor(hour)).padStart(2, '0')}:30`
    const end = `${String(Math.floor(hour + 2)).padStart(2, '0')}:30`
    setError('')
    const draft = {
      _key: `new-${Date.now()}-${day}-${hour}`,
      tipo_atividade: selectedType,
      titulo: selectedType === 'DISCIPLINA' ? '' : weeklyActivityLabel(selectedType),
      disciplina_codigo: '',
      dia_semana: day,
      hora_inicio: start,
      hora_fim: end,
      observacoes: '',
    }
    setEditorItem(draft)
    completeGuideAction('open-plan-slot')
    if (selectedType === 'DISCIPLINA') loadDisciplineOptions(draft)
    else {
      setDisciplines([])
      setDisciplinesError('')
      setDisciplinesLoading(false)
    }
  }

  function openExistingItem(item) {
    setEditorItem(item)
    if (item.tipo_atividade === 'DISCIPLINA') loadDisciplineOptions(item)
    else {
      setDisciplines([])
      setDisciplinesError('')
      setDisciplinesLoading(false)
    }
  }

  function applyItems(candidateItems, replaceKey = null) {
    const baseItems = replaceKey
      ? items.filter((current) => current._key !== replaceKey)
      : items
    const uniqueCandidates = candidateItems.filter((candidate, index, all) => (
      all.findIndex((entry) => samePlanSlot(entry, candidate)) === index
      && !baseItems.some((entry) => samePlanSlot(entry, candidate))
    )).map((candidate, index) => {
      const identity = weeklyDisciplineIdentity(candidate)
      return {
        ...candidate,
        codigo: identity.codigo,
        grupo_disciplina: identity.grupo,
        _key: replaceKey && index === 0
          ? replaceKey
          : `draft-${Date.now()}-${index}-${Math.random().toString(36).slice(2)}`,
      }
    })

    const staged = [...baseItems]
    for (const candidate of uniqueCandidates) {
      const conflict = staged.find((current) => overlaps(current, candidate))
      if (conflict) {
        setError(`Esse horário se sobrepõe a “${conflict.titulo || weeklyActivityLabel(conflict.tipo_atividade)}”.`)
        return false
      }
      staged.push(candidate)
    }

    setItems(staged)
    setDirty(true)
    setFeedback(
      uniqueCandidates.length > 1
        ? 'Todos os encontros da disciplina foram adicionados. Use “Salvar plano” para persistir.'
        : 'Alteração aplicada. Use “Salvar plano” para persistir.',
    )
    setError('')
    return true
  }

  function removeItem(key) {
    const selectedItem = items.find((item) => item._key === key)
    const disciplineGroup = selectedItem?.tipo_atividade === 'DISCIPLINA'
      ? selectedItem.grupo_disciplina
      : ''
    setItems((current) => current.filter((item) => (
      disciplineGroup ? item.grupo_disciplina !== disciplineGroup : item._key !== key
    )))
    setDirty(true)
    setFeedback(
      disciplineGroup
        ? 'A disciplina e todos os seus encontros foram removidos do rascunho. Salve o plano para confirmar.'
        : 'Atividade removida do rascunho. Salve o plano para confirmar.',
    )
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
      const payload = items.map(({ tipo_atividade, titulo, dia_semana, hora_inicio, hora_fim, observacoes }) => ({
        tipo_atividade,
        titulo: tipo_atividade === 'DISCIPLINA' ? titulo : weeklyActivityLabel(tipo_atividade),
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
      completeGuideAction('save-plan')
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
        <div ref={planGridGuideRef} className="week-page__schedule-builder">
          <div className="schedule-filters">
            {activityTypes.map((type) => (
              <button key={type.value} className={`schedule-filter schedule-filter--${type.tone}${selectedType === type.value ? ' is-active' : ''}`} type="button" onClick={() => setSelectedType(type.value)}>{type.label}</button>
            ))}
          </div>

          {loading ? <p className="week-page__loading">Carregando plano...</p> : (
            <ScheduleGrid entries={items} onSelectSlot={openNewItem} onSelectEntry={openExistingItem} />
          )}
        </div>

        <CargaPlanejada
          horasDisciplinas={disciplineHours}
          horasEstagio={internshipHours}
          horasOutras={otherHours}
        />

        {feedback && <p className="week-page__feedback is-success" role="status">{feedback}</p>}
        {error && <p className="week-page__feedback is-error" role="alert">{error}</p>}

        <button ref={planSaveGuideRef} className="primary-button week-page__save" type="button" disabled={!dirty || saving || loading} onClick={persistPlan}>
          <Save size={15} />{saving ? 'Salvando...' : 'Salvar plano'}
        </button>
      </div>
      <BottomNav active="plano" />
      {editorItem && (
        <PlanItemDialog
          key={editorItem._key}
          item={editorItem}
          disciplines={disciplines}
          disciplinesLoading={disciplinesLoading}
          disciplinesError={disciplinesError}
          planItems={items}
          onClose={() => setEditorItem(null)}
          onSave={applyItems}
          onDelete={removeItem}
        />
      )}
    </main>
  )
}

export default Semana
