const activityLabels = {
  DISCIPLINA: 'Disciplina',
  ESTAGIO: 'Estágio',
  OUTRO: 'Outra atividade',
}

export function weeklyActivityLabel(type) {
  return activityLabels[type] || 'Atividade'
}
