export function taxa(value) {
  return value == null ? 'Sem resultados' : `${value.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`
}
