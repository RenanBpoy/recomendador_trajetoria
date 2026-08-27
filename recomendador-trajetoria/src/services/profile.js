import { apiDelete, apiGet, apiPatch, apiPut, apiUpload } from './api'
import {
  getAccessToken,
  getStoredAuth,
  updateStoredProfile,
  updateStoredUser,
} from './auth'
import { invalidateAcademicCache } from './academic'
import { cachedSessionRequest, setSessionCache } from './sessionCache'

const PROFILE_TTL = 10 * 60 * 1000

function profileCacheKey() {
  const auth = getStoredAuth()
  return `${auth?.usuario?.id || auth?.perfil?.id || 'sem-usuario'}:profile:current`
}

function syncProfile(profile) {
  updateStoredProfile(profile)
  setSessionCache(profileCacheKey(), profile, PROFILE_TTL)
  return profile
}

export function getCurrentProfile({ force = false } = {}) {
  return cachedSessionRequest(
    profileCacheKey(),
    () => apiGet('/perfil', getAccessToken()).then(syncProfile),
    { ttlMs: PROFILE_TTL, force },
  )
}

export async function saveSelectedCurriculum(ppcId) {
  const profile = await apiPut('/perfil/ppc', { ppc_id: Number(ppcId) }, getAccessToken())
  invalidateAcademicCache()
  return syncProfile(profile)
}

export async function updatePersonalData(data) {
  const profile = await apiPatch('/perfil/dados-pessoais', data, getAccessToken())
  return syncProfile(profile)
}

export async function requestEmailChange(email) {
  const result = await apiPut('/perfil/email', { email }, getAccessToken())
  if (!result.confirmacao_necessaria) updateStoredUser({ email: result.email_solicitado })
  return result
}

export function updatePassword(senha, confirmacaoSenha) {
  return apiPut(
    '/perfil/senha',
    { senha, confirmacao_senha: confirmacaoSenha },
    getAccessToken(),
  )
}

export async function uploadAvatar(file) {
  const profile = await apiUpload('/perfil/avatar', file, getAccessToken())
  return syncProfile(profile)
}

export async function deleteAvatar() {
  const profile = await apiDelete('/perfil/avatar', getAccessToken())
  return syncProfile(profile)
}
