import { Navigate, useLocation } from 'react-router-dom'
import { hasActiveSession } from '../../services/auth'

function RequireAuth({ children }) {
  const location = useLocation()

  if (!hasActiveSession()) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return children
}

export default RequireAuth
