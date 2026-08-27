import { BookOpenCheck, Check, Search, Trash2, X } from 'lucide-react'
import { useMemo, useState } from 'react'
import './EquivalencePicker.css'

function statusTone(status) {
  const normalized = String(status || '').toLocaleUpperCase('pt-BR')
  if (normalized.includes('APROVADO') || normalized.includes('DISPENSA')) return 'approved'
  if (normalized.includes('TRANC')) return 'interrupted'
  return 'unavailable'
}

function EquivalencePicker({
  target,
  currentMapping,
  candidates,
  loading,
  busy,
  error,
  onClose,
  onSelect,
  onRemove,
}) {
  const [search, setSearch] = useState('')

  const visibleCandidates = useMemo(() => {
    const term = search.trim().toLocaleLowerCase('pt-BR')
    if (!term) return candidates
    return candidates.filter((candidate) => (
      `${candidate.codigo_original} ${candidate.nome_original}`
        .toLocaleLowerCase('pt-BR')
        .includes(term)
    ))
  }, [candidates, search])

  if (!target) return null

  const targetName = target.disciplina_nome || target.nome_no_ppc
  const targetDescription = target.eh_dcg
    ? `Vaga ${target.slot_ordem} de ${target.total_slots} · ${target.carga_horaria} h`
    : `${target.disciplina_codigo || 'Componente obrigatório'} · ${target.carga_horaria} h`

  return (
    <div className="equivalence-picker__backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="equivalence-picker"
        role="dialog"
        aria-modal="true"
        aria-labelledby="equivalence-picker-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="equivalence-picker__handle" />
        <header className="equivalence-picker__header">
          <span className="equivalence-picker__heading-icon"><BookOpenCheck size={20} /></span>
          <div>
            <small>Vincular disciplina do histórico</small>
            <strong id="equivalence-picker-title">{targetName}</strong>
            <span>{targetDescription}</span>
          </div>
          <button type="button" className="equivalence-picker__close" onClick={onClose} aria-label="Fechar seleção">
            <X size={18} />
          </button>
        </header>

        {currentMapping && (
          <div className="equivalence-picker__current">
            <div>
              <small>Disciplina vinculada</small>
              <strong>{currentMapping.nome_original}</strong>
              <span>{currentMapping.codigo_original} · {currentMapping.carga_horaria} h · {currentMapping.ano}/{currentMapping.semestre}</span>
            </div>
            <button type="button" onClick={onRemove} disabled={busy} aria-label="Remover disciplina vinculada">
              <Trash2 size={16} />
            </button>
          </div>
        )}

        <label className="equivalence-picker__search">
          <Search size={15} />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar nas disciplinas não mapeadas"
            aria-label="Buscar disciplina no histórico"
          />
        </label>

        <p className="equivalence-picker__hint">
          São mostradas as disciplinas do histórico que não foram reconhecidas como obrigatórias deste PPC.
        </p>

        {error && <p className="equivalence-picker__error" role="alert">{error}</p>}

        <div className="equivalence-picker__list">
          {loading && <p className="equivalence-picker__empty">Carregando disciplinas do histórico...</p>}
          {!loading && visibleCandidates.map((candidate) => {
            const tone = statusTone(candidate.situacao)
            const similarity = candidate.similaridade_nome === null
              ? null
              : Math.round(candidate.similaridade_nome * 100)
            return (
              <button
                key={candidate.id}
                type="button"
                className={`equivalence-option equivalence-option--${tone}`}
                disabled={!candidate.selecionavel || busy}
                onClick={() => onSelect(candidate.id)}
              >
                <span className="equivalence-option__icon"><Check size={16} /></span>
                <span className="equivalence-option__copy">
                  <strong>{candidate.nome_original}</strong>
                  <small>
                    {candidate.codigo_original} · {candidate.carga_horaria} h · {candidate.ano}/{candidate.semestre}
                  </small>
                  <em>{candidate.motivo_indisponibilidade || candidate.situacao}</em>
                </span>
                {similarity !== null && <span className="equivalence-option__match">{similarity}%</span>}
              </button>
            )
          })}
          {!loading && visibleCandidates.length === 0 && (
            <p className="equivalence-picker__empty">
              Nenhuma disciplina não mapeada foi encontrada. Carregue ou revise seu histórico escolar.
            </p>
          )}
        </div>
      </section>
    </div>
  )
}

export default EquivalencePicker
