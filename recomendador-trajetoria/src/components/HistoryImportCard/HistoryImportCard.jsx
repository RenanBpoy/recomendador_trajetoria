import { Check, FileUp, Link2, TriangleAlert, X } from 'lucide-react'
import { useRef } from 'react'
import {
  useFirstAccessGuideAction,
  useFirstAccessGuideTarget,
} from '../FirstAccessGuide/FirstAccessGuideContext'
import './HistoryImportCard.css'

function HistoryImportCard({ importData, busy, error, onUpload, onReview }) {
  const inputRef = useRef(null)
  const uploadGuideRef = useFirstAccessGuideTarget('first-access-history-upload')
  const completeGuideAction = useFirstAccessGuideAction()
  const suggestions = importData?.itens?.filter(
    (item) => item.status_correspondencia === 'SUGERIDA' && item.correspondencia_id,
  ) || []

  async function handleFile(event) {
    const [file] = event.target.files
    if (file) {
      const uploaded = await onUpload(file)
      if (uploaded) completeGuideAction('history-uploaded')
    }
    event.target.value = ''
  }

  return (
    <section className="history-import" aria-labelledby="history-import-title">
      <div className="history-import__intro">
        <span className="history-import__icon"><FileUp size={19} /></span>
        <div>
          <h2 id="history-import-title">Encontrou alguma inconsistência?</h2>
          <p>Carregue seu histórico para reconhecer disciplinas feitas com outro código.</p>
        </div>
      </div>

      <input
        ref={inputRef}
        className="history-import__input"
        type="file"
        accept="application/pdf,.pdf"
        onChange={handleFile}
      />
      <button
        ref={uploadGuideRef}
        className="history-import__upload"
        type="button"
        disabled={busy}
        onClick={() => inputRef.current?.click()}
      >
        {busy ? 'Lendo histórico...' : importData ? 'Enviar outro histórico' : 'Carregar histórico em PDF'}
      </button>

      {error && <p className="history-import__error" role="alert">{error}</p>}

      {importData && (
        <div className="history-import__result">
          <div className="history-import__file">
            <Link2 size={14} />
            <span><strong>{importData.nome_arquivo}</strong><small>PPC {importData.ppc_ano_documento}</small></span>
          </div>
          <div className="history-import__summary" aria-label="Resultado da leitura">
            <span><strong>{importData.identificados}</strong> identificadas</span>
            <span><strong>{importData.requerem_confirmacao}</strong> para revisar</span>
            <span><strong>{importData.nao_identificados}</strong> sem vínculo</span>
          </div>
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="history-import__suggestions">
          <h3><TriangleAlert size={14} /> Confirme estas semelhanças</h3>
          {suggestions.map((item) => (
            <article key={item.correspondencia_id}>
              <div>
                <strong>{item.nome_original}</strong>
                <small>pode corresponder a {item.disciplina_nome}</small>
              </div>
              <span>{Math.round(item.confianca_correspondencia * 100)}%</span>
              <button
                type="button"
                aria-label={`Confirmar ${item.nome_original}`}
                disabled={busy}
                onClick={() => onReview(item.correspondencia_id, 'confirmar')}
              ><Check size={14} /></button>
              <button
                type="button"
                aria-label={`Rejeitar ${item.nome_original}`}
                disabled={busy}
                onClick={() => onReview(item.correspondencia_id, 'rejeitar')}
              ><X size={14} /></button>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

export default HistoryImportCard
