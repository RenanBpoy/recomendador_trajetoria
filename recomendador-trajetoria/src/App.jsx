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
import Professores from './pages/Professores/Professores'
import PerfilProfessor from './pages/Professores/PerfilProfessor'
import Disciplinas from './pages/Disciplinas/Disciplinas'
import DisciplinaDetalhe from './pages/Disciplinas/DisciplinaDetalhe'
import DiarioClasse from './pages/DiariosClasse/DiarioClasse'
import TambemAnalisamos from './pages/TambemAnalisamos/TambemAnalisamos'
import RequireAuth from './components/RequireAuth/RequireAuth'
import { FirstAccessGuideProvider } from './components/FirstAccessGuide/FirstAccessGuide'
import LoadingScreen from './components/LoadingScreen/LoadingScreen'

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
          <Route path="/tambem-analisamos" element={protectedPage(<TambemAnalisamos />)} />
          <Route path="/professores" element={protectedPage(<Professores />)} />
          <Route path="/professores/:id" element={protectedPage(<PerfilProfessor />)} />
          <Route path="/disciplinas" element={protectedPage(<Disciplinas />)} />
          <Route path="/disciplinas/:codigo" element={protectedPage(<DisciplinaDetalhe />)} />
          <Route path="/diarios-classe" element={protectedPage(<Disciplinas diarios />)} />
          <Route path="/diarios-classe/disciplina/:codigo" element={protectedPage(<DisciplinaDetalhe diarios />)} />
          <Route path="/diarios-classe/:id" element={protectedPage(<DiarioClasse />)} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
        <LoadingScreen />
      </FirstAccessGuideProvider>
    </BrowserRouter>
  )
}

export default App
