import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Login from './pages/Login/Login'
import Cadastro from './pages/Cadastro/Cadastro'
import Home from './pages/Home/Home'
import Grade from './pages/Grade/Grade'
import Calendario from './pages/Calendario/Calendario'
import Perfil from './pages/Perfil/PerfilPage'
import Semana from './pages/Semana/Semana'
import HorarioDisponivel from './pages/HorarioDisponivel/HorarioDisponivel'
import Questionario from './pages/Questionario/Questionario'
import Recomendacao from './pages/Recomendacao/Recomendacao'
import RequireAuth from './components/RequireAuth/RequireAuth'
import { FirstAccessGuideProvider } from './components/FirstAccessGuide/FirstAccessGuide'

const protectedPage = (page) => <RequireAuth>{page}</RequireAuth>

function App() {
  return (
    <BrowserRouter>
      <FirstAccessGuideProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/cadastro" element={<Cadastro />} />
          <Route path="/home" element={protectedPage(<Home />)} />
          <Route path="/grade" element={protectedPage(<Grade />)} />
          <Route path="/calendario" element={protectedPage(<Calendario />)} />
          <Route path="/perfil" element={protectedPage(<Perfil />)} />
          <Route path="/semana" element={protectedPage(<Semana />)} />
          <Route path="/horario-disponivel" element={protectedPage(<HorarioDisponivel />)} />
          <Route path="/questionario" element={protectedPage(<Questionario />)} />
          <Route path="/recomendacao" element={protectedPage(<Recomendacao />)} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </FirstAccessGuideProvider>
    </BrowserRouter>
  )
}

export default App
