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
  if (component?.tipo_componente === 'BLOCO_DCG') return true
  return [component?.disciplina_nome, component?.nome_no_ppc]
    .filter(Boolean)
    .some((name) => normalizeStatus(name).includes('DISCIPLINA COMPLEMENTAR DE GRADUACAO'))
}

function mappingKey(componentId, slotOrder) {
  return `${componentId}:${slotOrder}`
}

export function expandCurriculumComponents(components) {
  return components.flatMap((component) => {
    if (!isComplementaryGraduationComponent(component)) {
      return [{
        ...component,
        chave_grade: String(component.id),
        ppc_componente_id: component.id,
        slot_ordem: 1,
        total_slots: 1,
        eh_dcg: false,
      }]
    }

    const totalSlots = Math.max(1, Math.ceil(Number(component.carga_horaria || 0) / 60))
    return Array.from({ length: totalSlots }, (_, index) => {
      const slotOrder = index + 1
      const remainingHours = Number(component.carga_horaria || 0) - index * 60
      return {
        ...component,
        id: `${component.id}-dcg-${slotOrder}`,
        chave_grade: `${component.id}-dcg-${slotOrder}`,
        ppc_componente_id: component.id,
        slot_ordem: slotOrder,
        total_slots: totalSlots,
        carga_horaria_original: component.carga_horaria,
        carga_horaria: Math.min(60, Math.max(remainingHours, 0)) || 60,
        nome_exibicao: `${component.nome_no_ppc} ${slotOrder}`,
        eh_dcg: true,
      }
    })
  })
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
  if (status.includes('APROVADO') || status.includes('DISPENSADO') || status.includes('DISPENSA')) {
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

export function buildCurriculumProgress(components, history, manualMappings = []) {
  const latest = latestHistoryByDiscipline(history)
  const mappings = new Map(
    manualMappings.map((mapping) => [
      mappingKey(mapping.ppc_componente_id, mapping.slot_ordem),
      mapping,
    ]),
  )

  return expandCurriculumComponents(components)
    .map((component) => {
      const automaticAttempt = component.eh_dcg
        ? null
        : latest.get(disciplineKey(component.disciplina_codigo)) || null
      const manualMapping = mappings.get(
        mappingKey(component.ppc_componente_id, component.slot_ordem),
      ) || null
      const manualAttempt = manualMapping ? {
        disciplina_codigo: component.disciplina_codigo || manualMapping.codigo_original,
        disciplina: component.disciplina_nome || component.nome_no_ppc,
        ano: manualMapping.ano,
        semestre: manualMapping.semestre,
        media_final: manualMapping.media,
        situacao_final: manualMapping.situacao,
        fonte: 'EQUIVALENCIA_MANUAL',
        disciplina_codigo_origem: manualMapping.codigo_original,
        disciplina_origem: manualMapping.nome_original,
        metodo_correspondencia: 'SELECAO_MANUAL',
      } : null
      const attempt = automaticAttempt || manualAttempt
      return {
        ...component,
        tentativa_mais_recente: attempt,
        estado_academico: academicStatusFor(attempt),
        equivalencia_manual: manualMapping,
      }
    })
}
