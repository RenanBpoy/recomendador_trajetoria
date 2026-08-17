import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Login from './pages/Login/Login'
import Cadastro from './pages/Cadastro/Cadastro'
import Home from './pages/Home/Home'
import Grade from './pages/Grade/Grade'
import Calendario from './pages/Calendario/Calendario'
import Perfil from './pages/Perfil/Perfil'
import Semana from './pages/Semana/Semana'
import HorarioDisponivel from './pages/HorarioDisponivel/HorarioDisponivel'
import RequireAuth from './components/RequireAuth/RequireAuth'

const protectedPage = (page) => <RequireAuth>{page}</RequireAuth>

function App() {
  return (
    <BrowserRouter>
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
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
