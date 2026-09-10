import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import CurriculumPanel from '../../components/CurriculumPanel/CurriculumPanel'
import EquivalencePicker from '../../components/EquivalencePicker/EquivalencePicker'
import HistoryImportCard from '../../components/HistoryImportCard/HistoryImportCard'
import { useStoredAuth } from '../../hooks/useStoredAuth'
import {
  getActiveHistoryImport,
  getCurriculum,
  getSchoolHistory,
  listEquivalenceCandidates,
  listManualEquivalences,
  listCurriculumComponents,
  removeManualEquivalence,
  reviewHistoryMatch,
  saveManualEquivalence,
  uploadSchoolHistory,
} from '../../services/academic'
import { courseName } from '../../utils/courses'
import './Grade.css'

function Grade() {
  const navigate = useNavigate()
  const profile = useStoredAuth()?.perfil
  const [curriculum, setCurriculum] = useState(null)
  const [components, setComponents] = useState([])
  const [history, setHistory] = useState([])
  const [manualMappings, setManualMappings] = useState([])
  const [importData, setImportData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [importBusy, setImportBusy] = useState(false)
  const [error, setError] = useState('')
  const [importError, setImportError] = useState('')
  const [pickerTarget, setPickerTarget] = useState(null)
  const [pickerCandidates, setPickerCandidates] = useState([])
  const [pickerLoading, setPickerLoading] = useState(false)
  const [pickerBusy, setPickerBusy] = useState(false)
  const [pickerError, setPickerError] = useState('')

  useEffect(() => {
    let active = true

    async function loadAcademicContext() {
      if (!profile?.curso_codigo || !profile?.matricula) {
        if (active) {
          setError('Entre novamente para carregar seu contexto acadêmico.')
          setLoading(false)
        }
        return
      }
      if (!profile?.ppc_id) {
        if (active) setLoading(false)
        return
      }

      try {
        const [selectedCurriculum, curriculumComponents, schoolHistory, activeImport, mappings] = await Promise.all([
          getCurriculum(profile.ppc_id),
          listCurriculumComponents(profile.ppc_id),
          getSchoolHistory(profile.matricula),
          getActiveHistoryImport(),
          listManualEquivalences(),
        ])
        if (!active) return
        setCurriculum(selectedCurriculum)
        setComponents(curriculumComponents)
        setHistory(schoolHistory)
        setImportData(activeImport)
        setManualMappings(mappings)
      } catch (requestError) {
        if (active) setError(requestError.message || 'Não foi possível carregar os dados acadêmicos.')
      } finally {
        if (active) setLoading(false)
      }
    }

    loadAcademicContext()
    return () => { active = false }
  }, [profile?.curso_codigo, profile?.matricula, profile?.ppc_id])

  async function refreshHistory() {
    const [updatedHistory, mappings] = await Promise.all([
      getSchoolHistory(profile.matricula),
      listManualEquivalences(),
    ])
    setHistory(updatedHistory)
    setManualMappings(mappings)
  }

  async function handleUpload(file) {
    setImportBusy(true)
    setImportError('')
    try {
      const result = await uploadSchoolHistory(file)
      setImportData(result)
      await refreshHistory()
      return true
    } catch (requestError) {
      setImportError(requestError.message || 'Não foi possível ler o histórico enviado.')
      return false
    } finally {
      setImportBusy(false)
    }
  }

  async function handleReview(correspondenceId, action) {
    setImportBusy(true)
    setImportError('')
    try {
      const result = await reviewHistoryMatch(correspondenceId, action)
      setImportData(result)
      await refreshHistory()
    } catch (requestError) {
      setImportError(requestError.message || 'Não foi possível revisar a correspondência.')
    } finally {
      setImportBusy(false)
    }
  }

  async function openEquivalencePicker(component) {
    setPickerTarget(component)
    setPickerCandidates([])
    setPickerError('')
    setPickerLoading(true)
    try {
      const candidates = await listEquivalenceCandidates(component.ppc_componente_id)
      setPickerCandidates(candidates)
    } catch (requestError) {
      setPickerError(requestError.message || 'Não foi possível listar as disciplinas do histórico.')
    } finally {
      setPickerLoading(false)
    }
  }

  async function handleSelectEquivalence(historyItemId) {
    if (!pickerTarget) return
    setPickerBusy(true)
    setPickerError('')
    try {
      await saveManualEquivalence(
        pickerTarget.ppc_componente_id,
        pickerTarget.slot_ordem,
        historyItemId,
      )
      setManualMappings(await listManualEquivalences())
      setPickerTarget(null)
    } catch (requestError) {
      setPickerError(requestError.message || 'Não foi possível salvar a equivalência.')
    } finally {
      setPickerBusy(false)
    }
  }

  async function handleRemoveEquivalence() {
    if (!pickerTarget) return
    setPickerBusy(true)
    setPickerError('')
    try {
      await removeManualEquivalence(
        pickerTarget.ppc_componente_id,
        pickerTarget.slot_ordem,
      )
      const [mappings, candidates] = await Promise.all([
        listManualEquivalences(),
        listEquivalenceCandidates(pickerTarget.ppc_componente_id),
      ])
      setManualMappings(mappings)
      setPickerCandidates(candidates)
    } catch (requestError) {
      setPickerError(requestError.message || 'Não foi possível remover a equivalência.')
    } finally {
      setPickerBusy(false)
    }
  }

  const currentPickerMapping = pickerTarget
    ? manualMappings.find((mapping) => (
      mapping.ppc_componente_id === pickerTarget.ppc_componente_id
      && mapping.slot_ordem === pickerTarget.slot_ordem
    )) || null
    : null

  return (
    <main className="mobile-page grade-page">
      <AppHeader title="Grade curricular" />
      <div className="grade-page__content">
        <section className="academic-context" aria-label="Contexto acadêmico">
          <div>
            <span>Curso do estudante</span>
            <strong>
              {courseName(profile?.curso_codigo)}
              {curriculum && ` - PPC ${curriculum.ano_versao}`}
            </strong>
          </div>
        </section>

        {!profile?.ppc_id && (
          <section className="grade-page__missing-ppc">
            <strong>Escolha seu PPC para montar a grade</strong>
            <p>A seleção fica salva no seu perfil e será usada em todos os cálculos de progresso.</p>
            <button type="button" onClick={() => navigate('/perfil')}>Escolher no perfil</button>
          </section>
        )}

        {error && <p className="form-feedback is-error" role="alert">{error}</p>}
        {profile?.ppc_id && (
          <CurriculumPanel
            components={components}
            history={history}
            manualMappings={manualMappings}
            loading={loading}
            onSelectEquivalence={openEquivalencePicker}
          />
        )}
        {profile?.ppc_id && (
          <HistoryImportCard
            importData={importData}
            busy={importBusy}
            error={importError}
            onUpload={handleUpload}
            onReview={handleReview}
          />
        )}
      </div>
      <BottomNav active="grade" />
      <EquivalencePicker
        key={pickerTarget?.chave_grade || 'closed-equivalence-picker'}
        target={pickerTarget}
        currentMapping={currentPickerMapping}
        candidates={pickerCandidates}
        loading={pickerLoading}
        busy={pickerBusy}
        error={pickerError}
        onClose={() => setPickerTarget(null)}
        onSelect={handleSelectEquivalence}
        onRemove={handleRemoveEquivalence}
      />
    </main>
  )
}

export default Grade
