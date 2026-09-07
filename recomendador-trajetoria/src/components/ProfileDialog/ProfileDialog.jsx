import { X } from 'lucide-react'
import { useEffect, useId } from 'react'
import './ProfileDialog.css'

function ProfileDialog({ title, subtitle, onClose, children, className = '', footer, dialogRef }) {
  const titleId = useId()

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return (
    <div
      className="profile-dialog__backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <section ref={dialogRef} className={`profile-dialog ${className}`.trim()} role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <header className="profile-dialog__header">
          <div>
            <h2 id={titleId}>{title}</h2>
            {subtitle && <p>{subtitle}</p>}
          </div>
          <button type="button" aria-label="Fechar" onClick={onClose}><X size={18} /></button>
        </header>
        <div className="profile-dialog__body">{children}</div>
        {footer && <footer className="profile-dialog__footer">{footer}</footer>}
      </section>
    </div>
  )
}

export default ProfileDialog
