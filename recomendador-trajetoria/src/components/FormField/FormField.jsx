import { Eye, EyeOff } from 'lucide-react'
import { useId, useState } from 'react'
import './FormField.css'

function FormField({ label, type = 'text', placeholder, name, icon: Icon, autoComplete, ...inputProps }) {
  const id = useId()
  const [visible, setVisible] = useState(false)
  const password = type === 'password'

  return (
    <label className="form-field" htmlFor={id}>
      <span className="form-field__label">{label}</span>
      <span className="form-field__control">
        <input
          id={id}
          name={name}
          type={password && visible ? 'text' : type}
          placeholder={placeholder}
          autoComplete={autoComplete}
          {...inputProps}
        />
        {password ? (
          <button
            type="button"
            className="form-field__icon"
            aria-label={visible ? 'Ocultar senha' : 'Mostrar senha'}
            onClick={() => setVisible((value) => !value)}
          >
            {visible ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        ) : Icon ? (
          <Icon className="form-field__static-icon" size={15} />
        ) : null}
      </span>
    </label>
  )
}

export default FormField
