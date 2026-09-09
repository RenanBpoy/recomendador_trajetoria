import MetricStrip from '../MetricStrip/MetricStrip'
import { taxa } from '../../utils/professores'

export default function ResumoResultados({ data, explicar = true }) {
  const reprovacao = data.resultados_avaliados ? Math.round(data.reprovados / data.resultados_avaliados * 1000) / 10 : null
  return <section className="consulta-resumo">
    <MetricStrip items={[{ value: taxa(data.taxa_aprovacao), label: 'aprovação', tone: 'green' }, { value: taxa(reprovacao), label: 'reprovação', tone: 'pink' }]} />
    <p>{data.aprovados} aprovações · {data.reprovados} reprovações · {data.outros_resultados} outros resultados.</p>
    {explicar && <details><summary>Como a taxa é calculada?</summary><p>Aprovações ÷ (aprovações + reprovações). Inclui reprovação por frequência; trancamentos, dispensas e situações incompletas ficam fora. Cada matrícula conta como uma tentativa, não como um aluno único.</p></details>}
  </section>
}
