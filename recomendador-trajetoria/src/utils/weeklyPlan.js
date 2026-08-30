const activityLabels = {
  DISCIPLINA: 'Disciplina',
  ESTAGIO: 'Estágio',
  OUTRO: 'Outra atividade',
}

export function weeklyActivityLabel(type) {
  return activityLabels[type] || 'Atividade'
}

const disciplineCodePattern = /^[a-z]{2,}[a-z0-9]*\d+[a-z0-9]*$/i

function normalizedKey(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toUpperCase()
}

export function weeklyDisciplineIdentity(item) {
  if (item?.tipo_atividade !== 'DISCIPLINA') {
    return { codigo: '', grupo: '' }
  }

  const observationParts = String(item.observacoes || '')
    .split('·')
    .map((part) => part.trim())
    .filter(Boolean)
  const observationCode = disciplineCodePattern.test(observationParts[0] || '')
    ? observationParts[0]
    : ''
  const code = String(item.codigo || item.disciplina_codigo || observationCode).trim()
  const classPart = observationParts.find((part) => /^turma\s+/i.test(part)) || ''
  const classCode = classPart.replace(/^turma\s+/i, '').trim()

  if (item.grupo_disciplina) {
    return { codigo: code, grupo: item.grupo_disciplina }
  }
  if (item.oferta_turma_id) {
    return { codigo: code, grupo: `oferta:${item.oferta_turma_id}` }
  }
  if (code && classCode) {
    return { codigo: code, grupo: `disciplina:${normalizedKey(code)}:turma:${normalizedKey(classCode)}` }
  }
  if (code) {
    return { codigo: code, grupo: `disciplina:${normalizedKey(code)}` }
  }

  const titleKey = normalizedKey(item.titulo || item.nome_exibicao)
  return {
    codigo: '',
    grupo: titleKey ? `disciplina-titulo:${titleKey}` : '',
  }
}
