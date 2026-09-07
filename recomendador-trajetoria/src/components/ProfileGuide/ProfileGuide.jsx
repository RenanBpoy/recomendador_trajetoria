import { useCallback, useEffect, useState } from 'react'
import presentingMascot from '../../assets/img/presenting.png'
import {
  completeProfileGuide,
  shouldShowFirstAccessGuide,
  shouldShowProfileGuide,
} from '../../services/firstAccessGuide'
import BalaoMascote from '../BalaoMascote/BalaoMascote'
import '../FirstAccessGuide/FirstAccessGuide.css'
import './ProfileGuide.css'

const steps = [

  {
    target: 'personal',
    placement: 'top',
    text: 'Começamos pelos seus dados pessoais. Aqui você pode conferir e atualizar seu nome, data de nascimento e e-mail.',
  },

  {
    target: 'academic',
    placement: 'top',
    text: 'Agora, seus dados acadêmicos. Aqui ficam seu curso, matrícula e o PPC usado para organizar sua grade. Se precisar, você também pode trocar o PPC por aqui.',
  },

  {
    target: 'privacy',
    placement: 'top',
    text: 'Se quiser cuidar da segurança da sua conta, é aqui. Em “Privacidade”, você encontra as opções relacionadas à sua senha de acesso.',
  },

  {
    target: 'help',
    placement: 'top',
    text: 'E se surgir alguma dúvida pelo caminho, passe em “Ajuda e suporte”. Lá você encontra orientações sobre a grade, o histórico e também pode rever nosso guia inicial. Eu sabia que você sentiria minha falta!',
  },

]

function ProfileGuide({ userId }) {
  const [open, setOpen] = useState(() => (
    Boolean(userId)
    && !shouldShowFirstAccessGuide(userId)
    && shouldShowProfileGuide(userId)
  ))
  const [stepIndex, setStepIndex] = useState(0)
  const [target, setTarget] = useState(null)
  const activeStep = steps[stepIndex]

  useEffect(() => {
    if (!open || !activeStep) return undefined
    const frame = window.requestAnimationFrame(() => {
      const element = document.querySelector(`[data-profile-guide="${activeStep.target}"]`)
      setTarget(element)
      element?.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })
    })
    return () => window.cancelAnimationFrame(frame)
  }, [activeStep, open])

  useEffect(() => {
    if (!open || !target) return undefined
    target.classList.add('first-access-guide__target', 'profile-guide__target')
    return () => target.classList.remove('first-access-guide__target', 'profile-guide__target')
  }, [open, target])

  const finishGuide = useCallback(() => {
    if (userId) completeProfileGuide(userId)
    setOpen(false)
  }, [userId])

  const advanceGuide = useCallback(() => {
    if (stepIndex >= steps.length - 1) {
      finishGuide()
      return
    }
    setTarget(null)
    setStepIndex((current) => current + 1)
  }, [finishGuide, stepIndex])

  if (!open) return null

  return (
    <>
      {target && <div className="first-access-guide__backdrop" aria-hidden="true" />}
      <BalaoMascote
        target={target}
        open={Boolean(target)}
        placement={activeStep.placement}
        imageSrc={presentingMascot}
        text={activeStep.text}
        nextLabel={stepIndex === steps.length - 1 ? 'Concluir apresentação do perfil' : 'Conhecer próximo card'}
        onNext={advanceGuide}
        onClose={finishGuide}
      />
    </>
  )
}

export default ProfileGuide
