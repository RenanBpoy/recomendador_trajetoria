import { Camera, UserRound } from 'lucide-react'
import { useRef } from 'react'
import './ProfileAvatar.css'

function ProfileAvatar({ name, url, busy = false, onSelect }) {
  const inputRef = useRef(null)

  function handleChange(event) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (file) onSelect(file)
  }

  return (
    <div className="profile-avatar-control">
      <div className="profile-avatar-control__image">
        {url ? <img src={url} alt={`Foto de ${name || 'perfil'}`} /> : <UserRound size={37} />}
      </div>
      <button
        type="button"
        aria-label={url ? 'Trocar foto do perfil' : 'Adicionar foto ao perfil'}
        title={url ? 'Trocar foto' : 'Adicionar foto'}
        disabled={busy}
        onClick={() => inputRef.current?.click()}
      >
        <Camera size={14} />
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        aria-hidden="true"
        tabIndex={-1}
        onChange={handleChange}
      />
    </div>
  )
}

export default ProfileAvatar
