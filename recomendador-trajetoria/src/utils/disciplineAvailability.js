function minutes(value) {
  const [hour, minute] = String(value).split(':').map(Number)
  return hour * 60 + minute
}

function overlaps(first, second) {
  return first.dia_semana === second.dia_semana
    && minutes(first.hora_inicio) < minutes(second.hora_fim)
    && minutes(second.hora_inicio) < minutes(first.hora_fim)
}

function belongsToEditedItem(planItem, editingItem) {
  if (!editingItem) return false
  if (planItem._key === editingItem._key) return true
  return Boolean(
    editingItem.grupo_disciplina
    && planItem.grupo_disciplina === editingItem.grupo_disciplina,
  )
}

export function findOfferingPlanConflicts(
  offering,
  planItems = [],
  editingItem = null,
) {
  const relevantPlanItems = planItems.filter(
    (planItem) => !belongsToEditedItem(planItem, editingItem),
  )

  return (offering.horarios || []).flatMap((schedule) => (
    relevantPlanItems
      .filter((planItem) => overlaps(schedule, planItem))
      .map((activity) => ({ schedule, activity }))
  ))
}

export function classifyOfferingsByPlan(
  offerings,
  planItems = [],
  editingItem = null,
) {
  const available = []
  const conflicting = []

  offerings.forEach((offering) => {
    const conflicts = findOfferingPlanConflicts(offering, planItems, editingItem)
    const entry = { offering, conflicts }
    if (conflicts.length) conflicting.push(entry)
    else available.push(entry)
  })

  return { available, conflicting }
}
