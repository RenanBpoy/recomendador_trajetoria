function disciplineKey(code) {
  return String(code || '').trim().toUpperCase()
}

function academicPeriodValue(entry) {
  return Number(entry?.ano || 0) * 10 + Number(entry?.semestre || 0)
}

function normalizeStatus(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/-+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toUpperCase()
}

function isComplementaryGraduationComponent(component) {
  return [component?.disciplina_nome, component?.nome_no_ppc]
    .filter(Boolean)
    .some((name) => normalizeStatus(name).includes('DISCIPLINAS COMPLEMENTARES DE GRADUACAO'))
}

export function latestHistoryByDiscipline(history) {
  const latest = new Map()

  for (const entry of history) {
    const key = disciplineKey(entry.disciplina_codigo)
    if (!key) continue

    const current = latest.get(key)
    if (!current || academicPeriodValue(entry) >= academicPeriodValue(current)) {
      latest.set(key, entry)
    }
  }

  return latest
}

export function academicStatusFor(entry) {
  if (!entry) return { key: 'pending', label: 'Pendente' }

  const status = normalizeStatus(entry.situacao_final)
  if (status.includes('APROVADO') || status.includes('DISPENSADO')) {
    return { key: 'approved', label: 'Aprovada' }
  }
  if (status.includes('REPROVADO')) {
    return { key: 'failed', label: 'Reprovada' }
  }
  if (status.includes('TRANCAMENTO')) {
    return { key: 'interrupted', label: 'Trancada' }
  }
  if (status.includes('CANCELAMENTO')) {
    return { key: 'interrupted', label: 'Cancelada' }
  }
  if (status.includes('NAO CONCLUIDA') || status.includes('INCOMPLETO')) {
    return { key: 'interrupted', label: 'Não concluída' }
  }
  return { key: 'pending', label: entry.situacao_final || 'Pendente' }
}

export function buildCurriculumProgress(components, history) {
  const latest = latestHistoryByDiscipline(history)

  return components
    .filter((component) => !isComplementaryGraduationComponent(component))
    .map((component) => {
      const attempt = latest.get(disciplineKey(component.disciplina_codigo)) || null
      return {
        ...component,
        tentativa_mais_recente: attempt,
        estado_academico: academicStatusFor(attempt),
      }
    })
}
