const ufsmCalendar = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'America/Sao_Paulo',
  year: 'numeric',
  month: 'numeric',
})

// Usado para separar o cache do navegador. A API decide o período das ofertas.
export function academicPeriodCacheKey(now = new Date()) {
  const parts = ufsmCalendar.formatToParts(now)
  const year = parts.find(({ type }) => type === 'year').value
  const month = Number(parts.find(({ type }) => type === 'month').value)
  return `${year}/${month <= 6 ? 1 : 2}`
}
