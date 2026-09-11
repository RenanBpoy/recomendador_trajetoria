export function formatRoundedHours(value) {
  const hours = Number(value)
  return Math.round(Number.isFinite(hours) ? hours : 0).toLocaleString('pt-BR')
}
